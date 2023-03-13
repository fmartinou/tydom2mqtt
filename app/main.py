#!/usr/bin/env python3
import asyncio
import time
from datetime import datetime
import os
import sys
import json
import socket
import websockets
from logger import logger
import logging

from mqtt_client import MQTT_Hassio
from tydomConnector import TydomWebSocketClient
from tydomMessagehandler import TydomMessageHandler

logger = logging.getLogger(__name__)

logger.info("Starting tydom2mqtt")

# Get config from env vars (+ fallback to default values)
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_PORT = os.getenv("MQTT_PORT", 1883)
MQTT_SSL = os.getenv("MQTT_SSL", False)
MQTT_USER = os.getenv("MQTT_USER", "")
TYDOM_ALARM_HOME_ZONE = os.getenv("TYDOM_ALARM_HOME_ZONE", 1)
TYDOM_ALARM_NIGHT_ZONE = os.getenv("TYDOM_ALARM_NIGHT_ZONE", 2)
TYDOM_ALARM_PIN = os.getenv("TYDOM_ALARM_PIN", None)
TYDOM_IP = os.getenv("TYDOM_IP", "mediation.tydom.com")
TYDOM_MAC = os.getenv("TYDOM_MAC", None)
TYDOM_PASSWORD = os.getenv("TYDOM_PASSWORD", None)


# Override configuration with hassio options file if found
override_configuration_for_hassio()

# Validate required configuration
validate_configuration()

# Create tydom client
tydom_client = TydomWebSocketClient(
    mac=TYDOM_MAC,
    host=TYDOM_IP,
    password=TYDOM_PASSWORD,
    alarm_pin=TYDOM_ALARM_PIN)
hassio = MQTT_Hassio(
    broker_host=MQTT_HOST,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASSWORD,
    mqtt_ssl=MQTT_SSL,
    home_zone=TYDOM_ALARM_HOME_ZONE,
    night_zone=TYDOM_ALARM_NIGHT_ZONE,
    tydom=tydom_client,
)


def loop_task():
    logger.debug("Starting main loop")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(hassio.connect())
    loop.run_until_complete(listen_tydom_forever(tydom_client))


def override_configuration_for_hassio():
    def hassio_options_file_path = "/data/options.json"

    try:
        with open(hassio_options_file_path) as f:

            logger.info(
                "Hassio environment detected: loading configuration from options.json....")

            try:
                data = json.load(f)
                logger.debug(data)

                if TYDOM_MAC in data and data["TYDOM_MAC"] != ""
                    TYDOM_MAC = data["TYDOM_MAC"]

                if TYDOM_IP in data and data["TYDOM_IP"] != ""
                    TYDOM_IP = data["TYDOM_IP"]

                if TYDOM_PASSWORD in data and data["TYDOM_PASSWORD"] != "":
                    TYDOM_PASSWORD = data["TYDOM_PASSWORD"]  # Tydom password

                if TYDOM_ALARM_PIN in data and data["TYDOM_ALARM_PIN"] != "":
                    TYDOM_ALARM_PIN = str(data["TYDOM_ALARM_PIN"]))

                if TYDOM_ALARM_HOME_ZONE in data and data["TYDOM_ALARM_HOME_ZONE"] != "":
                    TYDOM_ALARM_HOME_ZONE=data["TYDOM_ALARM_HOME_ZONE"]

                if TYDOM_ALARM_NIGHT_ZONE in data and data["TYDOM_ALARM_NIGHT_ZONE"] != "":
                    TYDOM_ALARM_NIGHT_ZONE=data["TYDOM_ALARM_NIGHT_ZONE"]

                if MQTT_HOST in data and data["MQTT_HOST"] != "":
                    MQTT_HOST=data["MQTT_HOST"]

                if MQTT_USER in data and data["MQTT_USER"] != "":
                    MQTT_USER=data["MQTT_USER"]

                if MQTT_PASSWORD in data and data["MQTT_PASSWORD"] != "":
                    MQTT_PASSWORD=data["MQTT_PASSWORD"]

                if MQTT_PORT in data and data["MQTT_PORT"] != "":
                    MQTT_PORT=data["MQTT_PORT"]

                if MQTT_SSL in data and data["MQTT_SSL"] != "":
                    MQTT_SSL=True

            except Exception as e:
                logger.error("Parsing error %s", e)

    except FileNotFoundError:
        logger.debug("Hassio environment not detected")

# Validate the resolved configuration.
def validate_configuration():
    if TYDOM_MAC == None or TYDOM_MAC == ""
        logger.error("Tydom MAC address must be defined")
        sys.exit(1)

    if TYDOM_PASSWORD == None or TYDOM_PASSWORD == "":
        logger.error("Tydom password must be defined")
        sys.exit(1)


# Listen to tydom events.
async def listen_tydom_forever(tydom_client):
    """
    Connect, then receive all server messages and pipe them to the handler, and reconnects if needed
    """

    while True:
        await asyncio.sleep(0)
        # outer loop restarted every time the connection fails
        try:
            await tydom_client.connect()
            logger.info("Tydom Client is connected to websocket and ready !")
            await tydom_client.setup()

            while True:
                # listener loop
                try:
                    incoming_bytes_str=await asyncio.wait_for(
                        tydom_client.connection.recv(),
                        timeout = tydom_client.refresh_timeout,
                    )
                    logger.debug("<<<<<<<<<< Receiving from tydom_client...")
                    logger.debug(incoming_bytes_str)

                except (
                    asyncio.TimeoutError,
                    websockets.exceptions.ConnectionClosed,
                ) as e:
                    logger.debug(e)
                    try:
                        pong=tydom_client.post_refresh()
                        await asyncio.wait_for(
                            pong, timeout = tydom_client.refresh_timeout
                        )
                        continue
                    except Exception as e:
                        logger.error(
                            "TimeoutError or websocket error - retrying connection in %s seconds...".format(
                                tydom_client.sleep_time))
                        logger.error("Error: %s", e)
                        await asyncio.sleep(tydom_client.sleep_time)
                        break
                logger.debug("Server said > %s".format(incoming_bytes_str))
                incoming_bytes_str

                handler = TydomMessageHandler(
                    incoming_bytes=incoming_bytes_str,
                    tydom_client=tydom_client,
                    mqtt_client=hassio,
                )
                try:
                    await handler.incomingTriage()
                except Exception as e:
                    logger.error("Tydom Message Handler exception : %s", e)

        except socket.gaierror:
            logger.info(
                "Socket error - retrying connection in %s sec (Ctrl-C to quit)".format(
                    tydom_client.sleep_time))
            await asyncio.sleep(tydom_client.sleep_time)
            continue
        except ConnectionRefusedError:
            logger.error(
                "Nobody seems to listen to this endpoint. Please check the URL."
            )
            logger.error(
                "Retrying connection in %s sec (Ctrl-C to quit)".format(
                    tydom_client.sleep_time
                )
            )
            await asyncio.sleep(tydom_client.sleep_time)
            continue


if __name__ == "__main__":
    loop_task()
