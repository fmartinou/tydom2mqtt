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
####################################### MQTT
tydom_topic = "+/tydom/#"
refresh_topic = "homeassistant/requests/tydom/refresh"
hostname = socket.gethostname()


# STOP = asyncio.Event()
class MQTT_Hassio():

    def __init__(self, broker_host, port, user, password, mqtt_ssl, home_zone=1, night_zone=2, tydom = None, tydom_alarm_pin = None):
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
            print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
            print('Attempting MQTT connection...')
            print('MQTT host : ', self.broker_host)
            print('MQTT user : ', self.user)
            adress = hostname+str(datetime.fromtimestamp(time.time()))
            # print(adress)

            client = MQTTClient(adress)
            # print(client)

            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.on_disconnect = self.on_disconnect
            # client.on_subscribe = self.on_subscribe

            client.set_auth_credentials(self.user, self.password)
            await client.connect(self.broker_host, self.port, self.ssl)

            self.mqtt_client = client
            return self.mqtt_client

        except Exception as e:
            print("MQTT connection Error : ", e)
            print('MQTT error, restarting in 8s...')
            await asyncio.sleep(8)
            await self.connect()


    def on_connect(self, client, flags, rc, properties):
        print("##################################")
        try:
            print("Subscribing to : ", tydom_topic)
            # client.subscribe('homeassistant/#', qos=0)
            client.subscribe(tydom_topic, qos=0)
        except Exception as e:
            print("Error on connect : ", e)
            

    async def on_message(self, client, topic, payload, qos, properties):
        # print('Incoming MQTT message : ', topic, payload)
        if ('update' in str(topic)):
#        if "update" in topic:
            print('Incoming MQTT update request : ', topic, payload)
            await self.tydom.get_data()
        elif ('kill' in str(topic)):
#        if "update" in topic:
            print('Incoming MQTT kill request : ', topic, payload)
            print('Exiting...')
            sys.exit()
        elif (topic == "homeassistant/requests/tydom/refresh"):
            print('Incoming MQTT refresh request : ', topic, payload)
            await self.tydom.post_refresh()
        elif (topic == "homeassistant/requests/tydom/scenarii"):
            print('Incoming MQTT scenarii request : ', topic, payload)
            await self.tydom.get_scenarii()

        elif (topic == "/tydom/init"):
            print('Incoming MQTT init request : ', topic, payload)
            await self.tydom.connect()

        # elif ('set_scenario' in str(topic)):
        #     print('Incoming MQTT set_scenario request : ', topic, payload)
        #     get_id = (topic.split("/"))[3] #extract id from mqtt
        #     # print(tydom, str(get_id), 'position', json.loads(payload))
        #     if not self.tydom.connection.open:
        #         print('Websocket not opened, reconnect...')
        #         await self.tydom.connect()
        #         await self.tydom.put_devices_data(str(get_id), 'position', str(json.loads(payload)))

        #     else:
        #         await self.tydom.put_devices_data(str(get_id), 'position', str(json.loads(payload)))
        
        elif 'set_positionCmd' in str(topic):
            print('Incoming MQTT set_positionCmd request : ', topic, payload)
            value = str(payload).strip('b').strip("'")
            get_id = (topic.split("/"))[2] #extract id from mqtt
            print(str(get_id), 'positionCmd', value)
            await Cover.put_positionCmd(tydom_client=self.tydom, cover_id=get_id, positionCmd=str(value))

        elif ('set_position' in str(topic)) and not ('set_positionCmd'in str(topic)):
            
            print('Incoming MQTT set_position request : ', topic, json.loads(payload))
            value = json.loads(payload)
            print(value)
            get_id = (topic.split("/"))[2] #extract id from mqtt
            await Cover.put_position(tydom_client=self.tydom, cover_id=get_id, position=str(value))



        elif ('set_alarm_state' in str(topic)) and not ('homeassistant'in str(topic)):
            # print(topic, payload, qos, properties)
            command = str(payload).strip('b').strip("'")
            get_id = (topic.split("/"))[2] #extract id from mqtt

            await Alarm.put_alarm_state(tydom_client=self.tydom, alarm_id=get_id, asked_state=command, home_zone=self.home_zone, night_zone=self.night_zone)

        else:
            pass
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print('MQTT incoming : ', topic, payload.decode())

    def on_disconnect(self, client, packet, exc=None):
        print('MQTT Disconnected !')
        print("##################################")
        # self.connect()
        

    def on_subscribe(self, client, mid, qos):
        print("MQTT is connected and suscribed ! =)", client)
        try:
            pyld = str(datetime.fromtimestamp(time.time()))
            client.publish('homeassistant/sensor/tydom/last_clean_startup', pyld, qos=1, retain=True)
        except Exception as e:
            print("on subscribe error : ", e)


