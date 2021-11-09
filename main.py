#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
import os
import sys
import json
import socket
import websockets
import uvloop

from mqtt_client import MQTT_Hassio
from tydomConnector import TydomWebSocketClient
from tydomMessagehandler import TydomMessageHandler

############ HASSIO ADDON
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

print('STARTING TYDOM2MQTT')

print('Dectecting environnement......')

uvloop.install()
print('uvloop init OK')
# DEFAULT VALUES


TYDOM_IP = 'mediation.tydom.com'
MQTT_HOST = 'localhost'
MQTT_PORT = 1883
MQTT_SSL = False
TYDOM_ALARM_PIN = None
TYDOM_ALARM_HOME_ZONE = 1
TYDOM_ALARM_NIGHT_ZONE = 2


try:
    with open('/data/options.json') as f:
        print('/data/options.json detected ! Hassio Addons Environnement : parsing options.json....')
        try:
            data = json.load(f)
            print(data)

            ####### CREDENTIALS TYDOM
            TYDOM_MAC = data['TYDOM_MAC'] #MAC Address of Tydom Box
            if data['TYDOM_IP'] != '':
                TYDOM_IP = data['TYDOM_IP'] #, 'mediation.tydom.com') # Local ip address, default to mediation.tydom.com for remote connexion if not specified

            TYDOM_PASSWORD = data['TYDOM_PASSWORD'] #Tydom password
            TYDOM_ALARM_PIN = data['TYDOM_ALARM_PIN']

            TYDOM_ALARM_HOME_ZONE = data['TYDOM_ALARM_HOME_ZONE']
            TYDOM_ALARM_NIGHT_ZONE = data['TYDOM_ALARM_NIGHT_ZONE']

            ####### CREDENTIALS MQTT
            if data['MQTT_HOST'] != '':
                MQTT_HOST = data['MQTT_HOST']
            
            MQTT_USER = data['MQTT_USER']
            MQTT_PASSWORD = data['MQTT_PASSWORD']

            if data['MQTT_PORT'] != 1883:
                MQTT_PORT = data['MQTT_PORT']

            if (data['MQTT_SSL'] == 'true') or (data['MQTT_SSL'] == True) :
                MQTT_SSL = True

        except Exception as e:
            print('Parsing error', e)

except FileNotFoundError :
    print("No /data/options.json, seems where are not in hassio addon mode.")
    ####### CREDENTIALS TYDOM
    TYDOM_MAC = os.getenv('TYDOM_MAC') #MAC Address of Tydom Box
    TYDOM_IP = os.getenv('TYDOM_IP', 'mediation.tydom.com') # Local ip address, default to mediation.tydom.com for remote connexion if not specified
    TYDOM_PASSWORD = os.getenv('TYDOM_PASSWORD') #Tydom password
    TYDOM_ALARM_PIN = os.getenv('TYDOM_ALARM_PIN')
    TYDOM_ALARM_HOME_ZONE = os.getenv('TYDOM_ALARM_HOME_ZONE', 1)
    TYDOM_ALARM_NIGHT_ZONE = os.getenv('TYDOM_ALARM_NIGHT_ZONE', 2)
    ####### CREDENTIALS MQTT
    MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
    MQTT_USER = os.getenv('MQTT_USER')
    MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
    MQTT_PORT = os.getenv('MQTT_PORT', 1883) #1883 #1884 for websocket without SSL
    MQTT_SSL = os.getenv('MQTT_SSL', False)


tydom_client = TydomWebSocketClient(mac=TYDOM_MAC, host=TYDOM_IP, password=TYDOM_PASSWORD, alarm_pin=TYDOM_ALARM_PIN)
hassio = MQTT_Hassio(broker_host=MQTT_HOST, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD, mqtt_ssl=MQTT_SSL, home_zone=TYDOM_ALARM_HOME_ZONE, night_zone=TYDOM_ALARM_NIGHT_ZONE, tydom=tydom_client)


def loop_task():
    print('Starting main loop_task')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hassio.connect())

    # tasks = [
    #     listen_tydom_forever(tydom_client)
    # ]

    loop.run_until_complete(listen_tydom_forever(tydom_client))


async def listen_tydom_forever(tydom_client):
    '''
        Connect, then receive all server messages and pipe them to the handler, and reconnects if needed
    '''

    while True:
        await asyncio.sleep(0)
        # # outer loop restarted every time the connection fails
        try:
            await tydom_client.connect()
            print("Tydom Client is connected to websocket and ready !")
            await tydom_client.setup()

            while True:
            # listener loop
                try:
                    incoming_bytes_str = await asyncio.wait_for(tydom_client.connection.recv(), timeout=tydom_client.refresh_timeout)
                    print('<<<<<<<<<< Receiving from tydom_client...')
                    # print(incoming_bytes_str)

                except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                    print(e)
                    try:
                        pong = tydom_client.post_refresh()
                        await asyncio.wait_for(pong, timeout=tydom_client.refresh_timeout)
                        # print('Ping OK, keeping connection alive...')
                        continue
                    except Exception as e:
                        print('TimeoutError or websocket error - retrying connection in {} seconds...'.format(tydom_client.sleep_time))
                        print('Error:', e)
                        await asyncio.sleep(tydom_client.sleep_time)
                        break
                # print('Server said > {}'.format(incoming_bytes_str))
                incoming_bytes_str
                        
                handler = TydomMessageHandler(incoming_bytes=incoming_bytes_str, tydom_client=tydom_client, mqtt_client=hassio)
                try:
                    await handler.incomingTriage()
                except Exception as e:
                    print('Tydom Message Handler exception :', e)
                                
        except socket.gaierror:
            print('Socket error - retrying connection in {} sec (Ctrl-C to quit)'.format(tydom_client.sleep_time))
            await asyncio.sleep(tydom_client.sleep_time)
            continue
        except ConnectionRefusedError:
            print('Nobody seems to listen to this endpoint. Please check the URL.')
            print('Retrying connection in {} sec (Ctrl-C to quit)'.format(tydom_client.sleep_time))
            await asyncio.sleep(tydom_client.sleep_time)
            continue


if __name__ == '__main__':
    loop_task()
