import asyncio
import websockets
import http.client
from requests.auth import HTTPDigestAuth
import sys
import logging
from http.client import HTTPResponse
from io import BytesIO
import urllib3
import json
import os
import base64
import time
from http.server import BaseHTTPRequestHandler
import ssl
from datetime import datetime
import subprocess, platform
import sdnotify


from cover import Cover
from alarm_control_panel import Alarm


# Thanks https://stackoverflow.com/questions/49878953/issues-listening-incoming-messages-in-websocket-client-on-python-3-6


# Logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# http.client.HTTPSConnection.debuglevel = 1
# http.client.HTTPConnection.debuglevel = 1

# Dicts
deviceAlarmKeywords = ['alarmMode','alarmState','alarmSOS','zone1State','zone2State','zone3State','zone4State','zone5State','zone6State','zone7State','zone8State','gsmLevel','inactiveProduct','zone1State','liveCheckRunning','networkDefect','unitAutoProtect','unitBatteryDefect','unackedEvent','alarmTechnical','systAutoProtect','sysBatteryDefect','zsystSupervisionDefect','systOpenIssue','systTechnicalDefect','videoLinkDefect', 'outTemperature']
# Device dict for parsing
device_dict = dict()
climateKeywords = ['temperature', 'authorization', 'hvacMode', 'setpoint']


class TydomWebSocketClient():

    def __init__(self, mac, password, host='mediation.tydom.com', mqtt_client=None):
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
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
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        print('""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""')
        print('TYDOM WEBSOCKET CONNECTION INITIALISING....                     ')


        if not (self.host == 'mediation.tydom.com'):
            test = None
            testlocal = None
            try:
                print('Testing if local Tydom hub IP is reachable....')
                testlocal = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', self.host), shell=True)
            except Exception as e:
                print('Local control is down, will try to fallback to remote....')

            try:
                # raise Exception ## Uncomment to pure lcoal IP mode
                print('Testing if mediation.tydom.com is reacheable...')
                test = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', 'mediation.tydom.com'), shell=True)
                print('mediation.tydom.com is reacheable ! Using it to prevent code 1006 deconnections from local ip for now.')
                self.host = 'mediation.tydom.com'
            except Exception as e:

                print('Remote control is down !')

                if (testlocal == None) :
                    print("Exiting to ensure systemd restart....")
                    sys.exit()
                else:
                    print('Fallback to local ip for that connection, except code 1006 deconnections every 60 seconds...')

           
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
                                                    extra_headers=websocketHeaders, ssl=websocket_ssl_context)

            # async with websockets.client.connect('wss://{}:443/mediation/client?mac={}&appli=1'.format(self.host, self.mac),
            #                                       extra_headers=websocketHeaders, ssl=websocket_ssl_context) as self.connection:

            while 1:
                await self.notify_alive()
                print('\o/ \o/ \o/ \o/ \o/ \o/ \o/ \o/ \o/ ')
                print("Tydom Websocket is Connected !", self.connection)
                return self.connection

        except Exception as e:
            print('Websocket def connect error')
            print(e)
            print('Exiting to ensure systemd restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Reconnecting...')
            # asyncio.sleep(8)
            # await self.connect()

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
                # await get_ping(self)
                # print('****** ping !')
                await self.post_refresh()
                await asyncio.sleep(40)


            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                print('Heartbeat error')
                print('Connection with server closed')
                print(e)
                print('Exiting to ensure systemd restart....')
                sys.exit() #Exit all to ensure systemd restart
                # print('Reconnecting...')
                # await self.connect()

# Send Generic GET message
    async def send_message(self, websocket, msg):
        if not self.connection.open:
            print('Exiting to ensure systemd restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Websocket not opened, reconnect...')
            # await self.connect()
   
        str = self.cmd_prefix + "GET " + msg +" HTTP/1.1\r\nContent-Length: 0\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"
        a_bytes = bytes(str, "ascii")
        await websocket.send(a_bytes)
        print('GET Command send to websocket')
        return 0

# Send Generic POST message
    async def send_post_message(self, websocket, msg):
        if not self.connection.open:
            print('Exiting to ensure systemd restart....')
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
            print('Exiting to ensure systemd restart....')
            sys.exit() #Exit all to ensure systemd restart
            # print('Websocket not opened, reconnect...')
            # await self.connect()

        # For shutter, value is the percentage of closing
        body="[{\"name\":\"" + name + "\",\"value\":\""+ value + "\"}]"
        # endpoint_id is the endpoint = the device (shutter in this case) to open.
        str_request = self.cmd_prefix + "PUT /devices/{}/endpoints/{}/data HTTP/1.1\r\nContent-Length: ".format(str(endpoint_id),str(endpoint_id))+str(len(body))+"\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"+body+"\r\n\r\n"
        a_bytes = bytes(str_request, "ascii")
        await self.connection.send(a_bytes)
        print('PUT request send to Websocket !')
        return 0

    # Run scenario
    async def put_scenarios(self, scenario_id):
        body=""
        # scenario_id is the id of scenario got from the get_scenarios command
        str_request = self.cmd_prefix + "PUT /scenarios/{} HTTP/1.1\r\nContent-Length: ".format(str(scenario_id))+str(len(body))+"\r\nContent-Type: application/json; charset=UTF-8\r\nTransac-Id: 0\r\n\r\n"+body+"\r\n\r\n"
        a_bytes = bytes(str_request, "ascii")
        await self.connection.send(a_bytes)
        # name = await websocket.recv()
        # parse_response(name)




    async def receiveMessage(self):
        '''
            Receiving all server messages and handling them
        '''
        while 1:

            bytes_str = await self.connection.recv()
            # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            # print(bytes_str)
            first = str(bytes_str[:40]) # Scanning 1st characters
            #Notify systemd watchdog
            await self.notify_alive()
            # n = sdnotify.SystemdNotifier()
            # n.notify("WATCHDOG=1")


            try:
                if ("refresh" in first):
                    print('OK refresh message detected !')
                    try:
                        pass
                        #ish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
                    except:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print('RAW INCOMING :')
                        print(bytes_str)
                        print('END RAW')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                elif ("PUT /devices/data" in first):
                    print('PUT /devices/data message detected !')
                    try:
                        incoming = self.parse_put_response(bytes_str)
                        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        await self.parse_response(incoming)
                        # print('PUT message processed !')
                        # print("##################################")
                        #ish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
                    except:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print('RAW INCOMING :')
                        print(bytes_str)
                        print('END RAW')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                elif ("scn" in first):
                    try:
                        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        incoming = get(bytes_str)
                        await self.parse_response(incoming)
                        print('Scenarii message processed !')
                        print("##################################")
                    except:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print('RAW INCOMING :')
                        print(bytes_str)
                        print('END RAW')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")            
                elif ("POST" in first):
                    try:
                        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        incoming = self.parse_put_response(bytes_str)
                        await self.parse_response(incoming)
                        print('POST message processed !')
                        # print("##################################")
                    except:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print('RAW INCOMING :')
                        print(bytes_str)
                        print('END RAW')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                elif ("HTTP/1.1" in first): #(bytes_str != 0) and 
                    response = self.response_from_bytes(bytes_str[len(self.cmd_prefix):])
                    incoming = response.data.decode("utf-8")
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    # print(incoming)
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    try:
                        # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        await self.parse_response(incoming)
                        # print('Pong !')
                        # print("##################################")
                    except:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print('RAW INCOMING :')
                        print(bytes_str)
                        print('END RAW')
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        # await parse_put_response(incoming)
                else:
                    print("Didn't detect incoming type, here it is :")
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print('RAW INCOMING :')
                    print(bytes_str)
                    print('END RAW')
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            except Exception as e:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print('receiveMessage error')
                print(e)
                print('Exiting to ensure systemd restart....')
                sys.exit() #Exit all to ensure systemd restart
                # print(bytes_str)
                # print('Reconnecting in 8s')
                # await asyncio.sleep(8)
                # await self.connect()





    # Basic response parsing. Typically GET responses + instanciate covers and alarm class for updating data
    async def parse_response(self, incoming):
        data = incoming
        msg_type = None
        first = str(data[:40])
        
        # Detect type of incoming data
        if (data != ''):
            if ("id" in first):
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print('Incoming message type : data detected')
                msg_type = 'msg_data'
            elif ("date" in first):
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print('Incoming message type : config detected')
                msg_type = 'msg_config'
            elif ("doctype" in first):
                print('Incoming message type : html detected (probable 404)')
                msg_type = 'msg_html'
                print(data)
            elif ("productName" in first):
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print('Incoming message type : Info detected')
                msg_type = 'msg_info'
                # print(data)        
            else:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print('Incoming message type : no type detected')
                print(first)

            if not (msg_type == None):
                try:
                    parsed = json.loads(data)
                    # print(parsed)
                    if (msg_type == 'msg_config'):
                        for i in parsed["endpoints"]:
                            # Get list of shutter
                            if i["last_usage"] == 'shutter':
                                # print('{} {}'.format(i["id_endpoint"],i["name"]))
                                device_dict[i["id_endpoint"]] = i["name"]
                                # TODO get other device type
                            if i["last_usage"] == 'alarm':
                                # print('{} {}'.format(i["id_endpoint"], i["name"]))
                                device_dict[i["id_endpoint"]] = "Tyxal Alarm"
                        print('Configuration updated')
                        
                    elif (msg_type == 'msg_data'):
                        # print(parsed)
                        for i in parsed:
                            attr = {}

                            if i["endpoints"][0]["error"] == 0:
                                for elem in i["endpoints"][0]["data"]:
                                    # Get full name of this id
                                    endpoint_id = i["endpoints"][0]["id"]
                                    # Element name
                                    elementName = elem["name"]
                                    # Element value
                                    elementValue = elem["value"]
                                    elementValidity = elem["validity"]
                                    # print(elementName,elementValue,elementValidity)
                                    # Get last known position (for shutter)
                                    if elementName == 'position' and elementValidity == 'upToDate':
                                        name_of_id = self.get_name_from_id(endpoint_id)
                                        if len(name_of_id) != 0:
                                            print_id = name_of_id
                                        else:
                                            print_id = endpoint_id
                                        # print('{} : {}'.format(print_id, elementValue))
                                        new_cover = "cover_tydom_"+str(endpoint_id)
                                        new_cover = Cover(id=endpoint_id,name=print_id, current_position=elementValue, attributes=i, mqtt=self.mqtt_client)
                                        new_cover.update()

                                    # Get last known state (for alarm) # NEW METHOD
                                    if elementName in deviceAlarmKeywords and elementValidity == 'upToDate':
                                        attr[elementName] = elementValue

                                # Get last known state (for alarm) # NEW METHOD
                                if attr != {}:
                                    # print(attr)
                                    state = None
                                    sos_state = False
                                    out = None

                                    if attr["alarmState"] and attr["alarmState"] == "ON":
                                        state = "triggered"
                                    if attr["alarmSOS"] and attr["alarmSOS"] == "true":
                                        state = "triggered"
                                        sos_state = True
                                    
                                    elif  attr ["alarmMode"] and attr ["alarmMode"]  == "ON":
                                        state = "armed_away"
                                    elif attr["alarmMode"] and attr["alarmMode"]  == "ZONE":
                                        state = "armed_home"
                                    elif attr["alarmMode"] and attr["alarmMode"]  == "OFF":
                                        state = "disarmed"
                                   
                                    out = attr["outTemperature"]

                                    if (sos_state == True):
                                        print("SOS !")
                                    if not (state == None):
                                        # print(state)
                                        alarm = "alarm_tydom_"+str(endpoint_id)
                                        # print("Alarm created / updated : "+alarm)
                                        alarm = Alarm(id=endpoint_id,name="Tyxal Alarm", current_state=state, out_temp=out, attributes=attr, sos=str(sos_state), mqtt=self.mqtt_client)
                                        alarm.update()


                                    # Get last known state (for alarm) # OLD Method, probably compatible if you have multiple alarms
                                    # if elementName in deviceAlarmKeywords:
                                    #     # print(i["endpoints"][0]["data"])
                                    #     alarm_data = '{} : {}'.format(elementName, elementValue)
                                    #     # print(alarm_data)
                                    #     # alarmMode  : ON or ZONE or OFF
                                    #     # alarmState : ON = Triggered
                                    #     # alarmSOS   : true = SOS triggered
                                    #     state = None
                                    #     sos_state = False
                                    #     out = None

                                    #     if alarm_data == "alarmState : ON":
                                    #         state = "triggered"
                                    #     if alarm_data == "alarmSOS : true":
                                    #         state = "triggered"
                                    #         sos_state = True
                                    #     if alarm_data == "alarmMode : ON":
                                    #         state = "armed_away"
                                    #     if alarm_data == "alarmMode : ZONE":
                                    #         state = "armed_home"
                                    #     if alarm_data == "alarmMode : OFF":
                                    #         state = "disarmed"

                                    #     if elementName == "outTemperature":
                                    #         out = elementValue
                                    #     else:
                                    #         attr[elementName] = [elementValue]
                                    #     #     attr[alarm_data]
                                    #         # print(attr)
                                    #     #device_dict[i["id_endpoint"]] = i["name"]
                                    #     if (sos_state == True):
                                    #         print("SOS !")
                                    #     if not (state == None):
                                    #         # print(state)
                                    #         alarm = "alarm_tydom_"+str(endpoint_id)
                                    #         # print("Alarm created / updated : "+alarm)
                                    #         alarm = Alarm(id=endpoint_id,name="Tyxal Alarm", current_state=state, out_temp=out, attributes=attr, sos=str(sos_state), mqtt=self.mqtt_client)
                                    #         alarm.update()

                    elif (msg_type == 'msg_html'):
                        print("HTML Response ?")
                    elif (msg_type == 'msg_info'):
                        pass
                    else:
                        # Default json dump
                        print()
                        print(json.dumps(parsed, sort_keys=True, indent=4, separators=(',', ': ')))
                except Exception as e:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                    print('Cannot parse response !')
                    # print('Response :')
                    # print(data)
                    if (e != 'Expecting value: line 1 column 1 (char 0)'):
                        print("Error : ", e)


    # PUT response DIRTY parsing
    def parse_put_response(self, bytes_str):
        # TODO : Find a cooler way to parse nicely the PUT HTTP response
        resp = bytes_str[len(self.cmd_prefix):].decode("utf-8")
        fields = resp.split("\r\n")
        fields = fields[6:]  # ignore the PUT / HTTP/1.1
        end_parsing = False
        i = 0
        output = str()
        while not end_parsing:
            field = fields[i]
            if len(field) == 0 or field == '0':
                end_parsing = True
            else:
                output += field
                i = i + 2
        parsed = json.loads(output)
        return json.dumps(parsed)

    ######### FUNCTIONS

    def response_from_bytes(self, data):
        sock = BytesIOSocket(data)
        response = HTTPResponse(sock)
        response.begin()
        return urllib3.HTTPResponse.from_httplib(response)

    def put_response_from_bytes(self, data):
        request = HTTPRequest(data)
        return request

    # Get pretty name for a device id
    def get_name_from_id(self, id):
        name = ""
        if len(device_dict) != 0:
            name = device_dict[id]
        return(name)

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
            print('Exiting to ensure systemd restart....')
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
        msg_type = 'ping'
        req = 'GET'
        await self.send_message(self.connection, msg_type)


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
            print('Exiting to ensure systemd restart....')
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
        statestr = msg #+' : '+str(datetime.fromtimestamp(time.time()))
        #Notify systemd watchdog
        n = sdnotify.SystemdNotifier()
        n.notify("WATCHDOG=1")
        print("Tydom HUB is still connected, systemd's watchdog notified...")

        # await self.POST_Hassio(sensorname='last_ping', state=statestr, friendlyname='Tydom Connection')
        # except Exception as e:
        #     print('Hassio sensor down !'+e)

    async def exiting(self):

        print("Exiting to ensure systemd restart....")
        statestr = 'Exiting...'+' : '+str(datetime.fromtimestamp(time.time()))

        # try:
        #     await self.POST_Hassio(sensorname='last_ping', state=statestr, friendlyname='Tydom connection')
        # except Exception as e:
        #     print('Hassio sensor down !'+e)
        sys.exit()

class BytesIOSocket:
    def __init__(self, content):
        self.handle = BytesIO(content)

    def makefile(self, mode):
        return self.handle

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        #self.rfile = StringIO(request_text)
        self.raw_requestline = request_text
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message
