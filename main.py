#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
import os
import sys


from mqtt_client import MQTT_Hassio
from tydom_websocket import TydomWebSocketClient



# from tendo import singleton
import socket



# me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running

# HOW TO service it :
# use supervisor !

# hostname = socket.gethostname()    
# IPAddr = socket.gethostbyname(hostname)
# print("Hostname :", hostname)
# print(IPAddr)

loop = asyncio.get_event_loop()


####### CREDENTIALS TYDOM
TYDOM_MAC = os.getenv('TYDOM_MAC') #MAC Address of Tydom Box
TYDOM_IP = os.getenv('TYDOM_IP', 'mediation.tydom.com') # Local ip address or mediation.tydom.com for remote connexion
TYDOM_PASSWORD = os.getenv('TYDOM_PASSWORD') #Tydom password

####### CREDENTIALS MQTT
MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')


####### OPTIONS
SYS_CONTEXT = os.getenv('SYS_CONTEXT', None) # None if you don't use systemd, preparing for docker....

def loop_task():

    tydom = None
    hassio = None

    # if (hostname == 'maison-ThinkPad-X240'): #Local hostname of your host machine
    #     local = True
    # else:
    #     local = False
#    local = False

    if (MQTT_HOST == None):
        MQTT_HOST = "localhost"
        MQTT_PORT = 1883 #1884 for websocket without SSL
        MQTT_SSL = False
    else:
        # host = remote_adress
        MQTT_HOST = MQTT_HOST
        MQTT_PORT = 8883 #8884 for websocket
        MQTT_SSL = True


    # Creating client object
    hassio = MQTT_Hassio(MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_SSL)
    # hassio_connection = loop.run_until_complete(hassio.connect())
    # Giving MQTT connection to tydom class for updating
    tydom = TydomWebSocketClient(mac=TYDOM_MAC, host=TYDOM_IP, password=TYDOM_PASSWORD, mqtt_client=hassio, sys_context=SYS_CONTEXT)

    # Start connection and get client connection protocol
    loop.run_until_complete(tydom.mqtt_client.connect())

    loop.run_until_complete(tydom.connect())
    # Giving back tydom client to MQTT client
    hassio.tydom = tydom

    print('Start websocket listener and heartbeat')
    if SYS_CONTEXT == 'systemd':
        import sdnotify
        # Inform systemd that we've finished our startup sequence...
        n = sdnotify.SystemdNotifier()
        n.notify("READY=1")

    tasks = [
        tydom.receiveMessage(),
        tydom.heartbeat()
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    # loop.run_forever()

if __name__ == '__main__':

    try:
        loop_task()
    except Exception as e:
        error = "FATAL ERROR ! {}".format(e)
        print(error)