import asyncio
import time
from datetime import datetime
import os
import sys


from mqtt_client import MQTT_Hassio
from tydom_websocket import TydomWebSocketClient

from tendo import singleton
me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running



loop = asyncio.get_event_loop()



####### CREDENTIALS TYDOM
mac = "" #MAC Address of Tydom Box
tydom_ip = "192.168.0.64" # Local ip address or mediation.tydom.com for remote connexion
password = "" #Tydom password

####### CREDENTIALS MQTT
mqtt_user = ''
mqtt_pass = ''

local = False

if (local == True):
    mqtt_host = "localhost"
    mqtt_port = 1883
    mqtt_ssl = False
else:
    # host = remote_adress
    mqtt_host = 'remotemqtt.org' #''
    mqtt_port = 8883
    mqtt_ssl = True


def loop_task():

    tydom = None
    hassio = None
    # Creating client object
    hassio = MQTT_Hassio(mqtt_host, mqtt_port, mqtt_user, mqtt_pass, mqtt_ssl)
    # hassio_connection = loop.run_until_complete(hassio.connect())
    # Giving MQTT connection to tydom class for updating
    tydom = TydomWebSocketClient(mac=mac, password=password, mqtt_client=hassio)

    # Start connection and get client connection protocol
    loop.run_until_complete(tydom.connect())
    loop.run_until_complete(tydom.mqtt_client.connect())
    # Giving back tydom client to MQTT client
    hassio.tydom = tydom

    print('Start websocket listener and heartbeat')

    tasks = [
        tydom.receiveMessage(),
        tydom.heartbeat()
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()

if __name__ == '__main__':
    
    try:
        loop_task()
    except Exception as e:
        error = "FATAL ERROR ! {}".format(e)
        print(error)
        try:
            hassio.publish('homeassistant/sensor/tydom/last_crash', error, qos=1, retain=True)
            print('Restarting loop...')
            loop_task()
        except:
            try:
                error = "BIG FATAL ERROR ! {}".format(e)
                hassio.publish('homeassistant/sensor/tydom/last_crash', error, qos=1, retain=True)
            except:
                print("Error : ", e)
            os.excel("tydom2mqtt_restarter.sh","")
            sys.exit(-1)
.sh","")
            sys.exit(-1)
        sys.exit(-1)
