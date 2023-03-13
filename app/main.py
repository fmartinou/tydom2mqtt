#!/usr/bin/env python3
import asyncio
import logging.config
import socket
import sys

import websockets

from configuration.Configuration import Configuration
from mqtt.MqttClient import MqttClient
from tydom.TydomClient import TydomClient
from tydom.TydomMessageHandler import TydomMessageHandler

# Setup logger configuration
logging.basicConfig(
    level='INFO',
    format='%(asctime)s - %(message)s')

# Init logger
logger = logging.getLogger(__name__)

logger.info("Starting tydom2mqtt")

# Load configuration from env vars (+ fallback to default values)
configuration = Configuration.load()

# Reconfigure logger after having loaded the configuration (because the log level can have changed)
for logger_handler in logging.root.handlers[:]:
    logging.root.removeHandler(logger_handler)
logging.basicConfig(
    level=configuration.log_level,
    format='%(asctime)s - %(name)-20s - %(levelname)-7s - %(message)s')

# Warning levels only for the following chatty modules (if not debug)
if configuration.log_level != 'DEBUG':
    logging.getLogger('gmqtt').setLevel(logging.WARNING)
    logging.getLogger('websockets').setLevel(logging.WARNING)


# Listen to tydom events.
async def listen_tydom():
    while True:
        try:
            await tydom_client.connect()
            await tydom_client.setup()

            while True:
                try:
                    incoming_bytes_str = await tydom_client.connection.recv()
                except websockets.exceptions.ConnectionClosed:
                    try:
                        await tydom_client.post_refresh()
                        continue
                    except Exception as e:
                        logger.error("Websocket error: %s", e)
                        break

                handler = TydomMessageHandler(
                    incoming_bytes=incoming_bytes_str,
                    tydom_client=tydom_client,
                    mqtt_client=mqtt_client,
                )
                try:
                    await handler.incoming_triage()
                except Exception as e:
                    logger.warning("Unable to handle message: %s", e)

        except socket.gaierror as e:
            logger.error("Socker error (%s)", e)
            sys.exit(1)
        except ConnectionRefusedError as e:
            logger.error("Connection refused (%s)", e)
            sys.exit(1)


# Create tydom client
tydom_client = TydomClient(
    mac=configuration.tydom_mac,
    host=configuration.tydom_ip,
    password=configuration.tydom_password,
    alarm_pin=configuration.tydom_alarm_pin)

# Create mqtt client
mqtt_client = MqttClient(
    broker_host=configuration.mqtt_host,
    port=configuration.mqtt_port,
    user=configuration.mqtt_user,
    password=configuration.mqtt_password,
    mqtt_ssl=configuration.mqtt_ssl,
    home_zone=configuration.tydom_alarm_home_zone,
    night_zone=configuration.tydom_alarm_night_zone,
    tydom=tydom_client,
)


async def main():
    await mqtt_client.connect()
    await listen_tydom()

asyncio.run(main())
