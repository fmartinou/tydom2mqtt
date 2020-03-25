
from cover import Cover
from alarm_control_panel import Alarm
from http.server import BaseHTTPRequestHandler
from http.client import HTTPResponse
import urllib3
from io import BytesIO
import json
import sys


# Dicts
deviceAlarmKeywords = ['alarmMode','alarmState','alarmSOS','zone1State','zone2State','zone3State','zone4State','zone5State','zone6State','zone7State','zone8State','gsmLevel','inactiveProduct','zone1State','liveCheckRunning','networkDefect','unitAutoProtect','unitBatteryDefect','unackedEvent','alarmTechnical','systAutoProtect','sysBatteryDefect','zsystSupervisionDefect','systOpenIssue','systTechnicalDefect','videoLinkDefect', 'outTemperature']
# Device dict for parsing
device_dict = dict()
climateKeywords = ['temperature', 'authorization', 'hvacMode', 'setpoint']


class TydomMessageHandler():


    def __init__(self, incoming_bytes, tydom_client):
            # print('New tydom incoming message')
            self.incoming_bytes = incoming_bytes
            self.tydom_client = tydom_client
            self.cmd_prefix = tydom_client.cmd_prefix
            self.mqtt_client = tydom_client.mqtt_client

    async def incomingTriage(self):

        bytes_str = self.incoming_bytes        
        incoming = None

        first = str(bytes_str[:40]) # Scanning 1st characters

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
            elif ("PUT /devices/data" in first) or ("/devices/cdata" in first):
                print('PUT /devices/data message detected !')
                try:
                    incoming = self.parse_put_response(bytes_str)

                    await self.parse_response(incoming)
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
            print('RAW :')
            print(bytes_str)
            print("Incoming payload :")
            print(incoming)
            print("Error :")
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
                                # device_dict[i["id_endpoint"]] = i["name"]
                                device_dict[i["id_device"]] = i["name"]
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
                                try:
                                    for elem in i["endpoints"][0]["data"]:
                                        # Get full name of this id
                                        # endpoint_id = i["endpoints"][0]["id"]
                                        endpoint_id = i["id"] # thanks @azrod 
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
                                            await new_cover.update()

                                        # Get last known state (for alarm) # NEW METHOD
                                        if elementName in deviceAlarmKeywords and elementValidity == 'upToDate':
                                            attr[elementName] = elementValue
                                except Exception as e:
                                    print('msg_data error in parsing !')
                                    print(e)
                                # Get last known state (for alarm) # NEW METHOD
                                if attr != {}:
                                    # print(attr)
                                    state = None
                                    sos_state = False
                                    out = None
                                    try:
                                        if 'alarmState' in attr and attr['alarmState'] == "ON":
                                            state = "triggered"
                                        if 'alarmSOS' in attr and attr['alarmSOS'] == "true":
                                            state = "triggered"
                                            sos_state = True                                                                               
                                        elif 'alarmMode' in attr and attr ["alarmMode"]  == "ON":
                                            state = "armed_away"
                                        elif 'alarmMode' in attr and attr["alarmMode"]  == "ZONE":
                                            state = "armed_home"
                                        elif 'alarmMode' in attr and attr["alarmMode"]  == "OFF":
                                            state = "disarmed"

                                        if 'outTemperature' in attr:
                                            out = attr["outTemperature"]

                                        if (sos_state == True):
                                            print("SOS !")

                                        if not (state == None):
                                            # print(state)
                                            alarm = "alarm_tydom_"+str(endpoint_id)
                                            # print("Alarm created / updated : "+alarm)
                                            alarm = Alarm(id=endpoint_id,name="Tyxal Alarm", current_state=state, out_temp=out, attributes=attr, sos=str(sos_state), mqtt=self.mqtt_client)
                                            await alarm.update()

                                    except Exception as e:
                                        print("Error in alarm parsing !")
                                        print(e)
                                        pass



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
                                    #     print(alarm_data)
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
                        print(parsed)


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


