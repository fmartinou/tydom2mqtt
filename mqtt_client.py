import asyncio
import time
import json
import socket
from datetime import datetime

from gmqtt import Client as MQTTClient

# Globals
####################################### MQTT
tydom_topic = "homeassistant/+/tydom/#"
refresh_topic = "homeassistant/requests/tydom/refresh"
hostname = socket.gethostname()

# STOP = asyncio.Event()
class MQTT_Hassio():

    def __init__(self, broker_host, port, user, password, mqtt_ssl, tydom = None):
        self.broker_host = broker_host
        self.port = port
        self.user = user
        self.password = password
        self.ssl = mqtt_ssl
        self.tydom = tydom
        self.mqtt_client = None


    async def connect(self):

        try:
            print('Attempting MQTT connection...')
            print(self.broker_host)
            client = MQTTClient(hostname)

            client.on_connect = self.on_connect
            client.on_message = self.on_message
            client.on_disconnect = self.on_disconnect
            client.on_subscribe = self.on_subscribe

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
            print("Error : ", e)
            

    async def on_message(self, client, topic, payload, qos, properties):


        if (topic == "homeassistant/requests/tydom/update"):
            print('Incoming MQTT update request : ', topic, payload)
            await self.tydom.get_data()
        elif (topic == "homeassistant/requests/tydom/refresh"):
            print('Incoming MQTT refresh request : ', topic, payload)
            await self.tydom.post_refresh()
        elif (topic == "homeassistant/requests/tydom/scenarii"):
            print('Incoming MQTT scenarii request : ', topic, payload)
            await self.tydom.get_scenarii()

        elif ('set_scenario' in str(topic)):
            print('Incoming MQTT set_scenario request : ', topic, payload)
            get_id = (topic.split("/"))[3] #extract id from mqtt
            # print(tydom, str(get_id), 'position', json.loads(payload))
            if not self.tydom.connection.open:
                print('Websocket not opened, reconnect...')
                await self.tydom.connect()
                await self.tydom.put_devices_data(str(get_id), 'position', str(json.loads(payload)))

            else:
                await self.tydom.put_devices_data(str(get_id), 'position', str(json.loads(payload)))
        elif ('set_position' in str(topic)):
            print('Incoming MQTT set_position request : ', topic, payload)
            get_id = (topic.split("/"))[3] #extract id from mqtt
            # print(tydom, str(get_id), 'position', json.loads(payload))
            if not self.tydom.connection.open:
                print('Websocket not opened, reconnect...')
                await self.tydom.connect()
                await self.tydom.put_devices_data(str(get_id), 'position', str(json.loads(payload)))

            else:
                await self.tydom.put_devices_data(str(get_id), 'position', str(json.loads(payload)))
        else:
            pass
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print('MQTT incoming : ', topic, payload.decode())

    def on_disconnect(self, client, packet, exc=None):
        print('MQTT Disconnected !')
        print("##################################")
        self.connect()    

    def on_subscribe(self, client, mid, qos):
        print("MQTT is connected and suscribed ! =)", client)
        pyld = 'Started !',str(datetime.fromtimestamp(time.time()))
        client.publish('homeassistant/sensor/tydom/last_clean_startup', pyld, qos=1, retain=True)
        # print('Requesting 1st data...')
        # await self.tydom.post_refresh()
        # await self.tydom.get_data()

                
    # def ask_exit(*args):
    #     STOP.set()
