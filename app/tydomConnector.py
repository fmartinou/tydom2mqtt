import asyncio
from asyncio import exceptions
import websockets
import http.client
from requests.auth import HTTPDigestAuth
import sys
import socket

import os
import base64
import time
import ssl
from datetime import datetime
import subprocess
import platform
from logger import logger
import logging

logger = logging.getLogger(__name__)

# Thanks
# https://stackoverflow.com/questions/49878953/issues-listening-incoming-messages-in-websocket-client-on-python-3-6


class TydomWebSocketClient:
    def __init__(self, mac, password, alarm_pin=None, host="mediation.tydom.com"):
        logger.info("Initialising TydomClient Class")

        self.password = password
        self.mac = mac
        self.host = host
        self.alarm_pin = alarm_pin
        self.connection = None
        self.remote_mode = True
        self.ssl_context = None
        self.cmd_prefix = "\x02"
        self.reply_timeout = 4
        self.ping_timeout = None
        self.refresh_timeout = 42
        # # ping_timeout=None is necessary on local connection to avoid 1006 erros
        self.sleep_time = 2
        self.incoming = None
        # if not (self.host == 'mediation.tydom.com'):
        #     test = None
        #     testlocal = None
        #     try:
        #         logger.info('Testing if local Tydom hub IP is reachable....')
        #         testlocal = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', self.host), shell=True)
        #     except Exception as e:
        #         logger.info('Local control is down, will try to fallback to remote....')
        #         try:
        #             logger.info('Testing if mediation.tydom.com is reacheable...')
        #             test = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', 'mediation.tydom.com'), shell=True)
        #             logger.info('mediation.tydom.com is reacheable ! Using it to prevent code 1006 deconnections from local ip for now.')
        #             self.host = 'mediation.tydom.com'
        #         except Exception as e:
        #             logger.info('Remote control is down !')

        #             if (testlocal == None) :
        #                 logger.info("Exiting to ensure restart....")
        #                 #sys.exit()

        # Set Host, ssl context and prefix for remote or local connection
        if self.host == "mediation.tydom.com":
            logger.info("Setting remote mode context.")
            self.remote_mode = True
            # self.ssl_context = None
            self.ssl_context = ssl._create_unverified_context()
            self.cmd_prefix = "\x02"
            self.ping_timeout = 40

        else:
            logger.info("Setting local mode context.")
            self.remote_mode = False
            self.ssl_context = ssl._create_unverified_context()
            self.cmd_prefix = ""
            self.ping_timeout = None

    async def connect(self):

        logger.info('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        logger.info("TYDOM WEBSOCKET CONNECTION INITIALISING....                     ")

        logger.info("Building headers, getting 1st handshake and authentication....")

        http_headers = {
            "Connection": "Upgrade",
            "Upgrade": "websocket",
            "Host": self.host + ":443",
            "Accept": "*/*",
            "Sec-WebSocket-Key": self.generate_random_key(),
            "Sec-WebSocket-Version": "13",
        }
        conn = http.client.HTTPSConnection(self.host, 443, context=self.ssl_context)

        # Get first handshake
        conn.request(
            "GET",
            "/mediation/client?mac={}&appli=1".format(self.mac),
            None,
            http_headers,
        )
        res = conn.getresponse()
        # Close HTTPS Connection
        conn.close()

        logger.debug("response headers")
        logger.debug(res.headers)
        logger.debug("response code")
        logger.debug(res.getcode())

        # read response
        logger.debug("response")
        logger.debug(res.read())
        res.read()

        # if res.getcode() is not 101:
        #     exit('Was not able to continue')

        # Get authentication
        websocket_headers = {}
        try:
            # Anecdotally, local installations are unauthenticated but we don't *know* that for certain
            # so we'll EAFP, try to use the header and fallback if we're unable.
            nonce = res.headers["WWW-Authenticate"].split(",", 3)
            # Build websocket headers
            websocket_headers = {"Authorization": self.build_digest_headers(nonce)}
        except AttributeError:
            pass

        logger.info("Upgrading http connection to websocket....")

        if self.ssl_context is not None:
            websocket_ssl_context = self.ssl_context
        else:
            websocket_ssl_context = True  # Verify certificate

        # outer loop restarted every time the connection fails
        logger.info(
            "Attempting websocket connection with tydom hub......................."
        )
        logger.info("Host Target : %s", self.host)
        """
            Connecting to webSocket server
            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        """
        try:
            self.connection = await websockets.connect(
                f"wss://{self.host}:443/mediation/client?mac={self.mac}&appli=1",
                extra_headers=websocket_headers,
                ssl=websocket_ssl_context,
                ping_timeout=None,
            )

            return self.connection
        except Exception as e:
            logger.error("Exception when trying to connect with websocket !")
            logger.error(e)
            logger.error(
                f"wss://{self.host}:443/mediation/client?mac={self.mac}&appli=1"
            )
            logger.error(websocket_headers)
            exit()

    # Utils

    # Generate 16 bytes random key for Sec-WebSocket-Keyand convert it to
    # base64
    def generate_random_key(self):
        return base64.b64encode(os.urandom(16))

    # Build the headers of Digest Authentication
    def build_digest_headers(self, nonce):
        digest_auth = HTTPDigestAuth(self.mac, self.password)
        chal = dict()
        chal["nonce"] = nonce[2].split('=', 1)[1].split('"')[1]
        chal["realm"] = "ServiceMedia" if self.remote_mode is True else "protected area"
        chal["qop"] = "auth"
        digest_auth._thread_local.chal = chal
        digest_auth._thread_local.last_nonce = nonce
        digest_auth._thread_local.nonce_count = 1
        return digest_auth.build_digest_header(
            "GET",
            "https://{host}:443/mediation/client?mac={mac}&appli=1".format(
                host=self.host, mac=self.mac
            ),
        )

    async def notify_alive(self, msg="OK"):
        # logger.info('Connection Still Alive !')
        pass
        # if self.sys_context == 'systemd':
        #     import sdnotify
        #     statestr = msg #+' : '+str(datetime.fromtimestamp(time.time()))
        #     #Notify systemd watchdog
        #     n = sdnotify.SystemdNotifier()
        #     n.notify("WATCHDOG=1")
        #     # logger.info("Tydom HUB is still connected, systemd's watchdog notified...")

    ###############################################################
    # Commands                                                    #
    ###############################################################

    # Send Generic  message

    async def send_message(self, method, msg):
        # logger.debug("%s %s", method, msg)

        str = (
            self.cmd_prefix
            + method
            + " "
            + msg
            + " HTTP/1.1\r\nContent-Length: 0\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
        )
        a_bytes = bytes(str, "ascii")
        if "pwd" not in msg:
            logger.info(">>>>>>>>>> Sending to tydom client..... %s %s", method, msg)
        else:
            logger.info(
                ">>>>>>>>>> Sending to tydom client..... %s %s", method, "secret msg"
            )

        await self.connection.send(a_bytes)
        # logger.debug(a_bytes)
        return 0

    # Give order (name + value) to endpoint
    async def put_devices_data(self, device_id, endpoint_id, name, value):

        # For shutter, value is the percentage of closing
        body = '[{"name":"' + name + '","value":"' + value + '"}]'
        # endpoint_id is the endpoint = the device (shutter in this case) to
        # open.
        str_request = (
            self.cmd_prefix
            + f"PUT /devices/{device_id}/endpoints/{endpoint_id}/data HTTP/1.1\r\nContent-Length: "
            + str(len(body))
            + "\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
            + body
            + "\r\n\r\n"
        )
        a_bytes = bytes(str_request, "ascii")
        # logger.debug(a_bytes)
        logger.info("Sending to tydom client..... %s %s", "PUT data", body)
        await self.connection.send(a_bytes)
        return 0

    async def put_alarm_cdata(self, device_id, alarm_id=None, value=None, zone_id=None):

        # Credits to @mgcrea on github !
        # AWAY # "PUT /devices/{}/endpoints/{}/cdata?name=alarmCmd HTTP/1.1\r\ncontent-length: 29\r\ncontent-type: application/json; charset=utf-8\r\ntransac-id: request_124\r\n\r\n\r\n{"value":"ON","pwd":{}}\r\n\r\n"
        # HOME "PUT /devices/{}/endpoints/{}/cdata?name=zoneCmd HTTP/1.1\r\ncontent-length: 41\r\ncontent-type: application/json; charset=utf-8\r\ntransac-id: request_46\r\n\r\n\r\n{"value":"ON","pwd":"{}","zones":[1]}\r\n\r\n"
        # DISARM "PUT /devices/{}/endpoints/{}/cdata?name=alarmCmd
        # HTTP/1.1\r\ncontent-length: 30\r\ncontent-type: application/json;
        # charset=utf-8\r\ntransac-id:
        # request_7\r\n\r\n\r\n{"value":"OFF","pwd":"{}"}\r\n\r\n"

        # variables:
        # id
        # Cmd
        # value
        # pwd
        # zones

        if self.alarm_pin is None:
            logger.warn("TYDOM_ALARM_PIN not set !")
            pass
        try:

            if zone_id is None:
                cmd = "alarmCmd"
                body = (
                    '{"value":"' + str(value) + '","pwd":"' + str(self.alarm_pin) + '"}'
                )
                # body= {"value":"OFF","pwd":"123456"}
            else:
                cmd = "zoneCmd"
                body = (
                    '{"value":"'
                    + str(value)
                    + '","pwd":"'
                    + str(self.alarm_pin)
                    + '","zones":"['
                    + str(zone_id)
                    + ']"}'
                )

            # str_request = self.cmd_prefix + "PUT /devices/{}/endpoints/{}/cdata?name={},".format(str(alarm_id),str(alarm_id),str(cmd)) + body +");"
            str_request = (
                self.cmd_prefix
                + "PUT /devices/{device}/endpoints/{alarm}/cdata?name={cmd} HTTP/1.1\r\nContent-Length: ".format(
                    device=str(device_id), alarm=str(alarm_id), cmd=str(cmd)
                )
                + str(len(body))
                + "\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
                + body
                + "\r\n\r\n"
            )

            a_bytes = bytes(str_request, "ascii")
            # logger.debug(a_bytes)
            logger.info("Sending to tydom client..... %s %s", "PUT cdata", body)

            await self.connection.send(a_bytes)
            return 0
        except Exception as e:
            logger.error("put_alarm_cdata ERROR !")
            logger.error(e)
            logger.error(a_bytes)

    # Get some information on Tydom

    async def get_info(self):
        msg_type = "/info"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)

    # Refresh (all)
    async def post_refresh(self):

        # logger.info("Refresh....")
        msg_type = "/refresh/all"
        req = "POST"
        await self.send_message(method=req, msg=msg_type)

    # Get the moments (programs)
    async def get_moments(self):
        msg_type = "/moments/file"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)

    # Get the scenarios
    async def get_scenarii(self):
        msg_type = "/scenarios/file"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)

    # Get a ping (pong should be returned)

    async def get_ping(self):
        msg_type = "/ping"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)
        logger.info("****** ping !")

    # Get all devices metadata

    async def get_devices_meta(self):
        msg_type = "/devices/meta"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)

    # Get all devices data

    async def get_devices_data(self):
        msg_type = "/devices/data"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)

    # List the device to get the endpoint id

    async def get_configs_file(self):
        msg_type = "/configs/file"
        req = "GET"
        await self.send_message(method=req, msg=msg_type)

    async def get_data(self):
        await self.get_configs_file()
        await asyncio.sleep(5)
        await self.get_devices_data()

    # Give order to endpoint
    async def get_device_data(self, id):
        # 10 here is the endpoint = the device (shutter in this case) to open.
        device_id = str(id)
        str_request = (
            self.cmd_prefix
            + f"GET /devices/{device_id}/endpoints/{device_id}/data HTTP/1.1\r\nContent-Length: 0\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
        )
        a_bytes = bytes(str_request, "ascii")
        await self.connection.send(a_bytes)
        # name = await self.recv()
        # parse_response(name)

    async def setup(self):
        """
        Sending heartbeat to server
        Ping - pong messages to verify connection is alive adn data is always up to date
        """
        logger.info("Requesting 1st data...")
        await self.get_info()
        logger.info("##################################")
        logger.info("##################################")
        await self.post_refresh()
        await self.get_data()
        # logger.info('Starting Heartbeating...')
        # while 1:
        #     await self.post_refresh()
        #     await asyncio.sleep(40)
