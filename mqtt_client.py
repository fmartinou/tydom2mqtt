import asyncio
import time
import json
import socket
import sys
from datetime import datetime
from gmqtt import Client as MQTTClient

from cover import Cover
from alarm_control_panel import Alarm

# Globals
# MQTT
from light import Light
from boiler import Boiler
from switch import Switch
from logger import logger
import logging

logger = logging.getLogger(__name__)
tydom_topic = "+/tydom/#"
refresh_topic = "homeassistant/requests/tydom/refresh"
hostname = socket.gethostname()


# STOP = asyncio.Event()
class MQTT_Hassio():

    def __init__(self, broker_host, port, user, password, mqtt_ssl,
                 home_zone=1, night_zone=2, tydom=None, tydom_alarm_pin=None):
        self.broker_host = broker_host
        self.port = port
        self.user = user
        self.password = password
        self.ssl = mqtt_ssl
        self.tydom = tydom
        self.tydom_alarm_pin = tydom_alarm_pin
        self.mqtt_client = None
        self.home_zone = home_zone
        self.night_zone = night_zone

    async def connect(self):

        try:
            logger.info('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
            logger.info('Attempting MQTT connection...')
            logger.info('MQTT host : %s', self.broker_host)
            logger.info('MQTT user : %s', self.user)
            adress = hostname + str(datetime.fromtimestamp(time.time()))
            # logger.info(adress)

            client = MQTTClient(adress)
            # logger.info(client)

            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.on_disconnect = self.on_disconnect
            # client.on_subscribe = self.on_subscribe

            client.set_auth_credentials(self.user, self.password)
            await client.connect(self.broker_host, self.port, self.ssl)

            self.mqtt_client = client
            return self.mqtt_client

        except Exception as e:
            logger.info("MQTT connection Error : %s", e)
            logger.info('MQTT error, restarting in 8s...')
            await asyncio.sleep(8)
            await self.connect()

    def on_connect(self, client, flags, rc, properties):
        logger.info("##################################")
        try:
            logger.info("Subscribing to : %s", tydom_topic)
            # client.subscribe('homeassistant/#', qos=0)
            client.subscribe('homeassistant/status', qos=0)
            client.subscribe(tydom_topic, qos=0)
        except Exception as e:
            logger.info("Error on connect : %s", e)

    async def on_message(self, client, topic, payload, qos, properties):
        logger.debug('Incoming MQTT message : %s %s', topic, payload)
        if ('update' in str(topic)):
            #        if "update" in topic:
            logger.info('Incoming MQTT update request : ', topic, payload)
            await self.tydom.get_data()
        elif ('kill' in str(topic)):
            #        if "update" in topic:
            logger.info('Incoming MQTT kill request : %s %s', topic, payload)
            logger.info('Exiting...')
            sys.exit()
        elif (topic == "homeassistant/requests/tydom/refresh"):
            logger.info('Incoming MQTT refresh request : %s %s', topic, payload)
            await self.tydom.post_refresh()
        elif (topic == "homeassistant/requests/tydom/scenarii"):
            logger.info('Incoming MQTT scenarii request : %s %s', topic, payload)
            await self.tydom.get_scenarii()
        elif (topic == "homeassistant/status" and payload.decode() == 'online'):
            await self.tydom.get_devices_data()
        elif (topic == "/tydom/init"):
            logger.info('Incoming MQTT init request : %s %s', topic, payload)
            await self.tydom.connect()

        # elif ('set_scenario' in str(topic)):
        #     logger.info('Incoming MQTT set_scenario request : %s %s', topic, payload)
        #     get_id = (topic.split("/"))[3] #extract id from mqtt
        #     # logger.debug("%s %s %s %s", tydom, str(get_id), 'position', json.loads(payload))
        #     if not self.tydom.connection.open:
        #         logger.info('Websocket not opened, reconnect...')
        #         await self.tydom.connect()
        # await self.tydom.put_devices_data(str(get_id), 'position',
        # str(json.loads(payload)))

        #     else:
        # await self.tydom.put_devices_data(str(get_id), 'position',
        # str(json.loads(payload)))

        elif 'set_positionCmd' in str(topic):
            logger.info('Incoming MQTT set_positionCmd request : %s %s', topic, payload)
            value = str(payload).strip('b').strip("'")

            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            logger.info("%s %s %s", str(get_id), 'positionCmd', value)
            await Cover.put_positionCmd(tydom_client=self.tydom, device_id=device_id, cover_id=endpoint_id,
                                        positionCmd=str(value))

        elif ('set_position' in str(topic)) and not ('set_positionCmd' in str(topic)):

            logger.info(
                'Incoming MQTT set_position request : %s %s',
                topic,
                json.loads(payload))
            value = json.loads(payload)
            # logger.debug(value)
            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Cover.put_position(tydom_client=self.tydom, device_id=device_id, cover_id=endpoint_id,
                                     position=str(value))

        elif 'set_levelCmd' in str(topic):
            logger.info('Incoming MQTT set_levelCmd request : %s %s', topic, payload)
            value = str(payload).strip('b').strip("'")

            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            logger.info("%s %s %s", str(get_id), 'levelCmd', value)
            await Light.put_level_cmd(tydom_client=self.tydom, device_id=device_id, light_id=endpoint_id,
                                      level_cmd=str(value))

        elif ('set_level' in str(topic)) and not ('set_levelCmd' in str(topic)):

            logger.info(
                'Incoming MQTT set_level request : %s %s',
                topic,
                json.loads(payload))
            value = json.loads(payload)
            # logger.debug(value)
            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Light.put_level(tydom_client=self.tydom, device_id=device_id, light_id=endpoint_id,
                                  level=str(value))

        elif ('set_alarm_state' in str(topic)) and not ('homeassistant' in str(topic)):
            # logger.debug("%s %s %s %s", topic, payload, qos, properties)
            command = str(payload).strip('b').strip("'")

            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Alarm.put_alarm_state(tydom_client=self.tydom, device_id=device_id, alarm_id=endpoint_id,
                                        asked_state=command, home_zone=self.home_zone, night_zone=self.night_zone)

        elif ('set_setpoint' in str(topic)):

            value = str(payload).strip('b').strip("'")
            logger.info('Incoming MQTT setpoint request : %s %s', topic, value)
            value = json.loads(payload)
            # logger.debug(value)
            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Boiler.put_temperature(tydom_client=self.tydom, device_id=device_id, boiler_id=endpoint_id,
                                         set_setpoint=str(value))

        elif 'set_hvacMode' in str(topic):

            value = str(payload).strip('b').strip("'")
            logger.info('Incoming MQTT set_hvacMode request : %s %s', topic, value)
            # logger.debug(value)
            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Boiler.put_hvac_mode(tydom_client=self.tydom, device_id=device_id, boiler_id=endpoint_id,
                                       set_hvac_mode=str(value))

        elif ('set_thermicLevel' in str(topic)):

            value = str(payload).strip('b').strip("'")
            logger.info('Incoming MQTT set_thermicLevel request : %s %s', topic, value)
            # logger.debug(value)
            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Boiler.put_thermic_level(tydom_client=self.tydom, device_id=device_id, boiler_id=endpoint_id,
                                           set_thermic_level=str(value))
        elif ('set_switch_state' in str(topic)) and not ('homeassistant' in str(topic)):
            # logger.debug("%s %s %s %s", topic, payload, qos, properties)
            command = str(payload).strip('b').strip("'")

            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            # This seems broken, but I'm not entirely clear what it is *meant* to do?
            await Switch.put_switch_state(tydom_client=self.tydom, device_id=device_id, switch_id=endpoint_id, state=command)

        elif 'set_levelCmdGate' in str(topic):
            logger.info('Incoming MQTT set_levelCmdGate request : %s %s', topic, payload)
            value = str(payload).strip('b').strip("'")

            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            logger.info("%s %s %s", str(get_id), 'levelCmd', value)
            await Switch.put_level_cmd_gate(tydom_client=self.tydom, device_id=device_id, switch_id=endpoint_id,
                                            level_cmd=str(value))

        elif ('set_levelGate' in str(topic)) and not ('set_levelCmd' in str(topic)):

            logger.info(
                'Incoming MQTT set_levelGate request : %s %s',
                topic,
                json.loads(payload))
            value = json.loads(payload)
            # logger.debug(value)
            get_id = (topic.split("/"))[2]  # extract ids from mqtt
            device_id = (get_id.split("_"))[0]  # extract id from mqtt
            endpoint_id = (get_id.split("_"))[1]  # extract id from mqtt

            await Switch.put_level_gate(tydom_client=self.tydom, device_id=device_id, switch_id=endpoint_id,
                                        level=str(value))

        else:
            pass
            # logger.debug(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # logger.debug('MQTT incoming : ', topic, payload.decode())

    def on_disconnect(self, client, packet, exc=None):
        logger.info('MQTT Disconnected !')
        logger.info("##################################")
        # self.connect()

    def on_subscribe(self, client, mid, qos):
        logger.info("MQTT is connected and suscribed ! =) %s", client)
        try:
            pyld = str(datetime.fromtimestamp(time.time()))
            client.publish(
                'homeassistant/sensor/tydom/last_clean_startup',
                pyld,
                qos=1,
                retain=True)
        except Exception as e:
            logger.error("on subscribe error : %s", e)
