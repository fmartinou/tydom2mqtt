from cover import Cover
from alarm_control_panel import Alarm
# from sensor import Sensor

from http.server import BaseHTTPRequestHandler
from http.client import HTTPResponse
import urllib3
from io import BytesIO
import json
import sys

# Dicts
deviceAlarmKeywords = ['alarmMode','alarmState','alarmSOS','zone1State','zone2State','zone3State','zone4State','zone5State','zone6State','zone7State','zone8State','gsmLevel','inactiveProduct','zone1State','liveCheckRunning','networkDefect','unitAutoProtect','unitBatteryDefect','unackedEvent','alarmTechnical','systAutoProtect','sysBatteryDefect','zsystSupervisionDefect','systOpenIssue','systTechnicalDefect','videoLinkDefect', 'outTemperature']
deviceAlarmDetailsKeywords = ['alarmSOS','zone1State','zone2State','zone3State','zone4State','zone5State','zone6State','zone7State','zone8State','gsmLevel','inactiveProduct','zone1State','liveCheckRunning','networkDefect','unitAutoProtect','unitBatteryDefect','unackedEvent','alarmTechnical','systAutoProtect','sysBatteryDefect','zsystSupervisionDefect','systOpenIssue','systTechnicalDefect','videoLinkDefect', 'outTemperature']

deviceCoverKeywords = ['position','onFavPos','thermicDefect','obstacleDefect','intrusion','battDefect']
deviceCoverDetailsKeywords = ['onFavPos','thermicDefect','obstacleDefect','intrusion','battDefect']

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
        if self.mqtt_client == None: #If not MQTT client, return incoming message to use it with anything.
            return bytes_str
        else:
            incoming = None
            first = str(bytes_str[:40]) # Scanning 1st characters
            try:
                if ("refresh" in first):
                    pass
                    # print('OK refresh message detected !')
                    # try:
                    #     pass
                    #     #ish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
                    # except:
                    #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    #     print('RAW INCOMING :')
                    #     print(bytes_str)
                    #     print('END RAW')
                    #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                elif ("PUT /devices/data" in first) or ("/devices/cdata" in first):
                    # print('PUT /devices/data message detected !')
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

    # Basic response parsing. Typically GET responses + instanciate covers and alarm class for updating data
    async def parse_response(self, incoming):
        data = incoming
        msg_type = None

        # try:
        #     parsed = json.loads(data)
        #     # print(parsed)
        # except Exception as e:
        #     if not ('Expecting' in e):
        #         print("Incoming Parse Error : ", e)
        #         print(parsed)

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
                print('Incoming message type : no type detected')
                print(first)

            if not (msg_type == None):
                try:                    
                    if (msg_type == 'msg_config'):
                        parsed = json.loads(data)
                        # print(parsed)
                        await self.parse_config_data(parsed=parsed)
                        
                    elif (msg_type == 'msg_data'):
                        parsed = json.loads(data)
                        # print(parsed)
                        await self.parse_devices_data(parsed=parsed)
                    elif (msg_type == 'msg_html'):
                        print("HTML Response ?")
                    elif (msg_type == 'msg_info'):
                        pass
                    else:
                        # Default json dump
                        print()
                        print(json.dumps(parsed, sort_keys=True, indent=4, separators=(',', ': ')))
                except Exception as e:
                    print('Cannot parse response !')
                    # print('Response :')
                    # print(data)
                    if (e != 'Expecting value: line 1 column 1 (char 0)'):
                        print("Error : ", e)
                        print(parsed)
            print('Incoming data parsed')
            return(0)
    async def parse_config_data(self, parsed):
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
        
    async def parse_devices_data(self, parsed):
        for i in parsed:
            if i["endpoints"][0]["error"] == 0:
                try:
                    attr_alarm = {}
                    attr_alarm_details = {}
                    attr_cover = {}
                    attr_cover_details = {}

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
                        ##### COVERS
                        if elementName in deviceCoverKeywords and elementValidity == 'upToDate': #NEW METHOD
                            
                        # if elementName == 'position' and elementValidity == 'upToDate':
                            # /*
                            # // https://github.com/mgcrea/homebridge-tydom/issues/2
                            # {name: 'thermicDefect', validity: 'upToDate', value: false},
                            # {name: 'position', validity: 'upToDate', value: 98},
                            # {name: 'onFavPos', validity: 'upToDate', value: false},
                            # {name: 'obstacleDefect', validity: 'upToDate', value: false},
                            # {name: 'intrusion', validity: 'upToDate', value: false},
                            # {name: 'battDefect', validity: 'upToDate', value: false}
                            # */
                            #TODO : Sensors with everything
                            print_id = None
                            name_of_id = self.get_name_from_id(endpoint_id)
                            if len(name_of_id) != 0:
                                print_id = name_of_id
                            else:
                                print_id = endpoint_id

                            attr_cover['id'] = i["id"]
                            attr_cover['cover_name'] = print_id
                            attr_cover['device_type'] = 'cover'
                            if elementName in deviceCoverDetailsKeywords:
                                attr_cover_details[elementName] = elementValue
                            else:
                                attr_cover[elementName] = elementValue
                            attr_cover['attributes'] = attr_cover_details
                        ##### ALARM

                        # Get last known state (for alarm) # NEW METHOD
                        elif elementName in deviceAlarmKeywords and elementValidity == 'upToDate':
                            # print(elementName,elementValue)
                            attr_alarm['id'] = i["id"]
                            attr_alarm['device_type'] = 'alarm_control_panel'
                            if elementName in deviceAlarmDetailsKeywords:
                                attr_alarm_details[elementName] = elementValue
                            else:

                                attr_alarm[elementName] = elementValue
                            attr_alarm['attributes'] = attr_alarm_details #KEEPING original details for attributes
                            # print(attr_alarm['attributes'])
                except Exception as e:
                    print('msg_data error in parsing !')
                    print(e)

                if 'device_type' in attr_cover and attr_cover['device_type'] == 'cover':
                    # print(attr_cover)
                    new_cover = "cover_tydom_"+str(endpoint_id)
                    new_cover = Cover(id=attr_cover['id'],name=attr_cover['cover_name'], current_position=attr_cover['position'], attributes=attr_cover['attributes'], mqtt=self.mqtt_client) #NEW METHOD
                    # new_cover = Cover(id=endpoint_id,name=print_id, current_position=elementValue, attributes=i, mqtt=self.mqtt_client)
                    await new_cover.update()

                # Get last known state (for alarm) # NEW METHOD
                elif 'device_type' in attr_alarm and attr_alarm['device_type'] == 'alarm_control_panel':
                    print(attr_alarm)
                    state = None
                    sos_state = False
                    maintenance_mode = False
                    out = None
                    try:
                        # {
                        # "name": "alarmState",
                        # "type": "string",
                        # "permission": "r",
                        # "enum_values": ["OFF", "DELAYED", "ON", "QUIET"]
                        # },
                        # {
                        # "name": "alarmMode",
                        # "type": "string",
                        # "permission": "r",
                        # "enum_values": ["OFF", "ON", "TEST", "ZONE", "MAINTENANCE"]
                        # }

                        if ('alarmState' in attr_alarm and attr_alarm['alarmState'] == "ON") or ('alarmState' in attr_alarm and attr_alarm['alarmState']) == "QUIET":
                            state = "triggered"
                        
                        elif 'alarmState' in attr_alarm and attr_alarm['alarmState'] == "DELAYED":
                            state = "pending"

                        if 'alarmSOS' in attr_alarm['attributes'] and attr_alarm['attributes']['alarmSOS'] == "true":
                            state = "triggered"
                            sos_state = True

                        elif 'alarmMode' in attr_alarm and attr_alarm ["alarmMode"]  == "ON":
                            state = "armed_away"
                        elif 'alarmMode' in attr_alarm and attr_alarm["alarmMode"]  == "ZONE":
                            state = "armed_home"
                        elif 'alarmMode' in attr_alarm and attr_alarm["alarmMode"]  == "OFF":
                            state = "disarmed"
                        elif 'alarmMode' in attr_alarm and attr_alarm["alarmMode"]  == "MAINTENANCE":
                            maintenance_mode = True
                            state = "disarmed"

                        if 'outTemperature' in attr_alarm:
                            out = attr_alarm["outTemperature"]

                        if (sos_state == True):
                            print("SOS !")

                        if not (state == None):
                            # print(state)
                            alarm = "alarm_tydom_"+str(endpoint_id)
                            # print("Alarm created / updated : "+alarm)
                            alarm = Alarm(id=attr_alarm['id'],name="Tyxal Alarm", current_state=state, attributes=attr_alarm['attributes'], mqtt=self.mqtt_client)
                            await alarm.update()

                    except Exception as e:
                        print("Error in alarm parsing !")
                        print(e)
                        pass



                else:
                    pass
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


