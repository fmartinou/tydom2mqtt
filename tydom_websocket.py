import asyncio
import websockets
import http.client
from requests.auth import HTTPDigestAuth
import sys
import logging

import os
import base64
import time
import ssl
from datetime import datetime
import subprocess, platform
# import aiohttp

from tydomMessagehandler import TydomMessageHandler

# Thanks https://stackoverflow.com/questions/49878953/issues-listening-incoming-messages-in-websocket-client-on-python-3-6


# Logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# http.client.HTTPSConnection.debuglevel = 1
# http.client.HTTPConnection.debuglevel = 1


class TydomWebSocketClient():

    def __init__(self, mac, password, host='mediation.tydom.com', mqtt_client=None):
        print('Initialising TydomClient Class')

        self.password = password
        self.mac = mac
        self.host = host
        self.mqtt_client = mqtt_client
        self.connection = None
        self.remote_mode = True
        self.ssl_context = None
        self.cmd_prefix = "\x02"

    async def connect(self):
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        print('TYDOM WEBSOCKET CONNECTION INITIALISING....                     ')


        # if not (self.host == 'mediation.tydom.com'):
        #     test = None
        #     testlocal = None
        #     try:
        #         print('Testing if local Tydom hub IP is reachable....')
        #         testlocal = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', self.host), shell=True)
        #     except Exception as e:
        #         print('Local control is down, will try to fallback to remote....')
        #         try:
        #             print('Testing if mediation.tydom.com is reacheable...')
        #             test = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', 'mediation.tydom.com'), shell=True)
        #             print('mediation.tydom.com is reacheable ! Using it to prevent code 1006 deconnections from local ip for now.')
        #             self.host = 'mediation.tydom.com'
        #         except Exception as e:
        #             print('Remote control is down !')

        #             if (testlocal == None) :
        #                 print("Exiting to ensure restart....")
        #                 sys.exit()

           
        # Set Host, ssl context and prefix for remote or local connection
        if self.host == "mediation.tydom.com":
            print('Setting remote mode context.')
            self.remote_mode = True
            self.ssl_context = None
            self.cmd_prefix = "\x02"
            
        else:
            print('Setting local mode context.')
            self.remote_mode = False
            self.ssl_context = ssl._create_unverified_context()
            self.cmd_prefix = ""

        print('Building headers, getting 1st handshake and authentication....')
        '''
            Connecting to webSocket server
            websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        '''
        httpHeaders =  {"Connection": "Upgrade",
                        "Upgrade": "websocket",
                        "Host": self.host + ":443",
                        "Accept": "*/*",
                        "Sec-WebSocket-Key": self.generate_random_key(),
                        "Sec-WebSocket-Version": "13"
                        }
        conn = http.client.HTTPSConnection(self.host, 443, context=self.ssl_context)
        # Get first handshake
        conn.request("GET", "/mediation/client?mac={}&appli=1".format(self.mac), None, httpHeaders)
        res = conn.getresponse()
        # Get authentication
        nonce = res.headers["WWW-Authenticate"].split(',', 3)
        # read response
        res.read()
        # Close HTTPS Connection
        conn.close()
        print('Upgrading http connection to websocket....')
        # Build websocket headers
        websocketHeaders = {'Authorization': self.build_digest_headers(nonce)}
        if self.ssl_context is not None:
            websocket_ssl_context = self.ssl_context
        else:
            websocket_ssl_context = True # Verify certificate


        try:
            print('Attempting websocket connection with tydom hub.......................')
            print('Host Target :')
            print(self.host)
            
            self.connection = await websockets.client.connect('wss://{}:443/mediation/client?mac={}&appli=1'.format(self.host, self.mac),
                                                    extra_headers=websocketHeaders, ssl=websocket_ssl_context, ping_timeout=None)

            # session = aiohttp.ClientSession()
            # self.connection = await session.ws_connect('wss://{}:443/mediation/client?mac={}&appli=1'.format(self.host, self.mac),
            #                                          extra_headers=websocketHeaders, ssl=websocket_ssl_context)


            # async with websockets.client.connect('wss://{}:443/mediation/client?mac={}&appli=1'.format(self.host, self.mac),
            #                                       extra_headers=websocketHeaders, ssl=websocket_ssl_context) as self.connection:

            while 1:
                await self.notify_alive()
                print('\o/ \o/ \o/ \o/ \o/ \o/ \o/ \o/ \o/ ')
                print("Tydom Client is connected to websocket and ready !", self.connection)
                return self.connection

        except Exception as e:
            print('Websocket def connect error')
            print(e)
            print('Exiting to ensure restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Reconnecting...')
            # asyncio.sleep(8)
            # await self.connect()

    async def receiveMessage(self):
        '''
            Receiving all server messages and pipe them to the handler
        '''
        while 1:
            incoming_bytes_str = await self.connection.recv()
            #Notify systemd watchdog
            await self.notify_alive()
            handler = TydomMessageHandler(incoming_bytes = incoming_bytes_str, tydom_client = self)
            try:
                await handler.incomingTriage()
            except Exception as e:
                print('Tydom Message Handler exception :', e)

    async def heartbeat(self):
        '''
        Sending heartbeat to server
        Ping - pong messages to verify connection is alive
        '''
        print('Requesting 1st data...')

        await self.get_info()
        print("##################################")
        print("##################################")
        await self.post_refresh()
        await self.get_data()
        while self.connection.open:
            try:
                # await self.connection.send('ping')
                # await self.get_ping()
                await self.post_refresh()
                await asyncio.sleep(40)
            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print('Connection with server closed')
                print(e)
                print('Exiting to ensure restart....')
                sys.exit() #Exit all to ensure systemd restart
                # print('Reconnecting...')
                # await self.connect()



############ Utils


# Send Generic GET message
    async def send_message(self, websocket, msg):
        if not self.connection.open:
            print('Exiting to ensure restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Websocket not opened, reconnect...')
            # await self.connect()
   
        str = self.cmd_prefix + "GET " + msg +" HTTP/1.1\r\nContent-Length: 0\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
        a_bytes = bytes(str, "ascii")
        await websocket.send(a_bytes)
        # print('GET Command send to websocket')
        # print (a_bytes)
        return 0

# Send Generic POST message
    async def send_post_message(self, websocket, msg):
        if not self.connection.open:
            print('Exiting to ensure restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Websocket not opened, reconnect...')
            # await self.connect()

        str = self.cmd_prefix + "POST " + msg +" HTTP/1.1\r\nContent-Length: 0\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
        a_bytes = bytes(str, "ascii")
        await websocket.send(a_bytes)
        # print('POST Command send to websocket')
        return 0

    # Give order (name + value) to endpoint
    async def put_devices_data(self, endpoint_id, name, value):
        if not self.connection.open:
            print('Exiting to ensure restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Websocket not opened, reconnect...')
            # await self.connect()

        # For shutter, value is the percentage of closing
        body="[{\"name\":\"" + name + "\",\"value\":\""+ value + "\"}]"
        # endpoint_id is the endpoint = the device (shutter in this case) to open.
        str_request = self.cmd_prefix + "PUT /devices/{}/endpoints/{}/data HTTP/1.1\r\nContent-Length: ".format(str(endpoint_id),str(endpoint_id))+str(len(body))+"\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"+body+"\r\n\r\n"
        a_bytes = bytes(str_request, "ascii")
        print(a_bytes)
        await self.connection.send(a_bytes)
        print('PUT /devices/data send to Websocket !')
        return 0

    async def put_alarm_cdata(self, alarm_id, pwd, value, zones = None):

        if not self.connection.open:
            print('Connection closed, exiting to ensure restart....')
            sys.exit()

        if zones != None:
            cmd = 'alarmCmd'
            body="[{\"pwd\":\"" + pwd + "\",\"value\":\""+ value + "\"}]"
        else:
            cmd = 'zoneCmd'
            body="[{\"pwd\":\"" + pwd + "\",\"value\":\""+ value + "\",\"zones\":\""+ zones + "\"}]"

        
        str_request = self.cmd_prefix + "PUT /devices/{}/endpoints/{}/cdata?name={} HTTP/1.1\r\nContent-Length: ".format(str(alarm_id),str(alarm_id),str(cmd))+str(len(body))+"\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"+body+"\r\n\r\n"
        a_bytes = bytes(str_request, "ascii")
        await self.connection.send(a_bytes)
        print('PUT /devices/data send to Websocket !')
        return 0


    # await client.put(`/devices/${deviceId}/endpoints/${endpointId}/cdata?name=alarmCmd`, {
      #     value: nextValue,
      #     pwd: pin
      #   });
    # await client.put(`/devices/${deviceId}/endpoints/${endpointId}/cdata?name=zoneCmd`, {
      #       value: nextValue,
      #       pwd: pin,
      #       zones: targetZones
      #     });
    # Run scenario
    async def put_scenarios(self, scenario_id):
        body=""
        # scenario_id is the id of scenario got from the get_scenarios command
        str_request = self.cmd_prefix + "PUT /scenarios/{} HTTP/1.1\r\nContent-Length: ".format(str(scenario_id))+str(len(body))+"\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"+body+"\r\n\r\n"
        a_bytes = bytes(str_request, "ascii")
        await self.connection.send(a_bytes)
        # name = await websocket.recv()
        # parse_response(name)
            
    # Generate 16 bytes random key for Sec-WebSocket-Keyand convert it to base64
    def generate_random_key(self):
        return base64.b64encode(os.urandom(16))

    # Build the headers of Digest Authentication
    def build_digest_headers(self, nonce):
        digestAuth = HTTPDigestAuth(self.mac, self.password)
        chal = dict()
        chal["nonce"] = nonce[2].split('=', 1)[1].split('"')[1]
        chal["realm"] = "ServiceMedia" if self.remote_mode is True else "protected area"
        chal["qop"] = "auth"
        digestAuth._thread_local.chal = chal
        digestAuth._thread_local.last_nonce = nonce
        digestAuth._thread_local.nonce_count = 1
        return digestAuth.build_digest_header('GET', "https://{}:443/mediation/client?mac={}&appli=1".format(self.host, self.mac))

    ###############################################################
    # Commands                                                    #
    ###############################################################

    # Get some information on Tydom
    async def get_info(self):
        msg_type = '/info'
        await self.send_message(self.connection, msg_type)

    # Refresh (all)
    async def post_refresh(self):
        if not (self.connection.open):
            print('Exiting to ensure restart....')
            sys.exit() #Exit all to ensure systemd restart
        else:
            # print("Refresh....")
            msg_type = '/refresh/all'
            # req = 'POST'
            await self.send_post_message(self.connection, msg_type)

    # Get the moments (programs)
    async def get_moments(self):
        msg_type = '/moments/file'
        req = 'GET'
        await self.send_message(self.connection, msg_type)

    # Get the scenarios
    async def get_scenarii(self):
        msg_type = '/scenarios/file'
        req = 'GET'
        await self.send_message(self.connection, msg_type)


    # Get a ping (pong should be returned)
    async def get_ping(self):
        msg_type = '/ping'
        req = 'GET'
        await self.send_message(self.connection, msg_type)
        print('****** ping !')



    # Get all devices metadata
    async def get_devices_meta(self):
        msg_type = '/devices/meta'
        req = 'GET'
        await self.send_message(self.connection, msg_type)


    # Get all devices data
    async def get_devices_data(self):
        msg_type = '/devices/data'
        req = 'GET'
        await self.send_message(self.connection, msg_type)


    # List the device to get the endpoint id
    async def get_configs_file(self):
        msg_type = '/configs/file'
        req = 'GET'
        await self.send_message(self.connection, msg_type)

    async def get_data(self):
        if not self.connection.open:
            print('get_data error !')
            # await self.exiting()wait self.exiting()
            print('Exiting to ensure restart....')
            sys.exit() #Exit all to ensure systemd restart

        else:
            await self.get_configs_file()
            await asyncio.sleep(2)
            await self.get_devices_data()

    # Give order to endpoint
    async def get_device_data(self, id):
        # 10 here is the endpoint = the device (shutter in this case) to open.
        str_request = self.cmd_prefix + "GET /devices/{}/endpoints/{}/data HTTP/1.1\r\nContent-Length: 0\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n".format(str(id),str(id))
        a_bytes = bytes(str_request, "ascii")
        await self.connection.send(a_bytes)
        # name = await websocket.recv()
        # parse_response(name)


    async def notify_alive(self, msg='OK'):
        # print('Connection Still Alive !')
        pass
        # if self.sys_context == 'systemd':
        #     import sdnotify
        #     statestr = msg #+' : '+str(datetime.fromtimestamp(time.time()))
        #     #Notify systemd watchdog
        #     n = sdnotify.SystemdNotifier()
        #     n.notify("WATCHDOG=1")
        #     # print("Tydom HUB is still connected, systemd's watchdog notified...")


