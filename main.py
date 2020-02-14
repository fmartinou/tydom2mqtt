#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
import os
import sys
import sdnotify


from mqtt_client import MQTT_Hassio
from tydom_websocket import TydomWebSocketClient

import socket


# HOW TO service it :
# use supervisor !

hostname = socket.gethostname()    
IPAddr = socket.gethostbyname(hostname)
print(hostname)
print(IPAddr)

loop = asyncio.get_event_loop()



####### CREDENTIALS TYDOM
mac = "" #MAC Address of Tydom Box
tydom_ip = "" # Local ip address (local mode is not used by default for now, but you can force it in tydom_websocket.py
password = "" #Tydom password

####### CREDENTIALS MQTT
mqtt_user = ''
mqtt_pass = ''


local = False



def loop_task():

    tydom = None
    hassio = None

    if (hostname == ''): #Local hostname of your host machine
        local = True
    else:
        local = False


    if (local == True):
        mqtt_host = "localhost"
        mqtt_port = 1883
        mqtt_ssl = False
    else:
        # host = remote_adress
        mqtt_host = '' #
        mqtt_port = 8883
        mqtt_ssl = True


    # Creating client object
    hassio = MQTT_Hassio(mqtt_host, mqtt_port, mqtt_user, mqtt_pass, mqtt_ssl)
    # hassio_connection = loop.run_until_complete(hassio.connect())
    # Giving MQTT connection to tydom class for updating
    tydom = TydomWebSocketClient(mac=mac, host=tydom_ip, password=password, mqtt_client=hassio)

    # Start connection and get client connection protocol
    loop.run_until_complete(tydom.mqtt_client.connect())

    loop.run_until_complete(tydom.connect())
    # Giving back tydom client to MQTT client
    hassio.tydom = tydom

    print('Start websocket listener and heartbeat')

    # Inform systemd that we've finished our startup sequence...
    n = sdnotify.SystemdNotifier()
    n.notify("READY=1")

    tasks = [
        tydom.receiveMessage(),
        tydom.heartbeat()
    ]

    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':

    
    try:
        loop_task()
    except Exception as e:
        error = "FATAL ERROR ! {}".format(e)
        print(error)
        n.notify("WATCHDOG=trigger")
