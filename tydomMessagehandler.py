from cover import Cover
from light import Light
from alarm_control_panel import Alarm
from sensors import sensor

from http.server import BaseHTTPRequestHandler
from http.client import HTTPResponse
import urllib3
from io import BytesIO
import json
import sys
import logging

_LOGGER = logging.getLogger(__name__)

# Dicts
deviceAlarmKeywords = ['alarmMode','alarmState','alarmSOS','zone1State','zone2State','zone3State','zone4State','zone5State','zone6State','zone7State','zone8State','gsmLevel','inactiveProduct','zone1State','liveCheckRunning','networkDefect','unitAutoProtect','unitBatteryDefect','unackedEvent','alarmTechnical','systAutoProtect','sysBatteryDefect','zsystSupervisionDefect','systOpenIssue','systTechnicalDefect','videoLinkDefect', 'outTemperature']
deviceAlarmDetailsKeywords = ['alarmSOS','zone1State','zone2State','zone3State','zone4State','zone5State','zone6State','zone7State','zone8State','gsmLevel','inactiveProduct','zone1State','liveCheckRunning','networkDefect','unitAutoProtect','unitBatteryDefect','unackedEvent','alarmTechnical','systAutoProtect','sysBatteryDefect','zsystSupervisionDefect','systOpenIssue','systTechnicalDefect','videoLinkDefect', 'outTemperature']

deviceLightKeywords = ['level','onFavPos','thermicDefect','battDefect','loadDefect','cmdDefect','onPresenceDetected','onDusk']
deviceLightDetailsKeywords = ['onFavPos','thermicDefect','battDefect','loadDefect','cmdDefect','onPresenceDetected','onDusk']

deviceDoorKeywords = ['openState']
deviceDoorDetailsKeywords = ['onFavPos','thermicDefect','obstacleDefect','intrusion','battDefect']

deviceCoverKeywords = ['position','onFavPos','thermicDefect','obstacleDefect','intrusion','battDefect']
deviceCoverDetailsKeywords = ['onFavPos','thermicDefect','obstacleDefect','intrusion','battDefect']

climateKeywords = ['temperature', 'authorization', 'hvacMode', 'setpoint']

# Device dict for parsing
device_name = dict()
device_endpoint = dict()
device_type = dict()
# Thanks @Max013 !

class TydomMessageHandler():


    def __init__(self, incoming_bytes, tydom_client, mqtt_client):
            # print('New tydom incoming message')
            self.incoming_bytes = incoming_bytes
            self.tydom_client = tydom_client
            self.cmd_prefix = tydom_client.cmd_prefix
            self.mqtt_client = mqtt_client

    async def incomingTriage(self):

        # if (data != ''):
        #     if ("Uri-Origin: /refresh/all" in first):
        #         pass
        #     elif ("Uri-Origin: /devices/data" in first):
        #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #         print('Incoming message type : data detected')
        #         msg_type = 'msg_data'
        #     elif ("Uri-Origin: /configs/" in first):
        #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #         print('Incoming message type : config detected')
        #         msg_type = 'msg_config'
        #     elif ("doctype" in first):
        #         print('Incoming message type : html detected (probable 404)')
        #         msg_type = 'msg_html'
        #         print(data)
        #     elif ("Uri-Origin: /info" in first):
        #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #         print('Incoming message type : Info detected')
        #         msg_type = 'msg_info'
        #         # print(data)        
        #     else:
        #         print('Incoming message type : no type detected')
        #         print(first)


        bytes_str = self.incoming_bytes        
        if self.mqtt_client == None: #If not MQTT client, return incoming message to use it with anything.
            return bytes_str
        else:
            incoming = None
            first = str(bytes_str[:40]) # Scanning 1st characters
            try:
                if ("Uri-Origin: /refresh/all" in first in first):
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
                        #print(parsed)
                        await self.parse_config_data(parsed=parsed)
                        
                    elif (msg_type == 'msg_data'):
                        parsed = json.loads(data)
                        #print(parsed)
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
            print('Incoming data parsed successfully !')
            return(0)

    async def parse_config_data(self, parsed):
        for i in parsed["endpoints"]:
            # Get list of shutter
            # print(i)
            if i["last_usage"] == 'shutter' or i["last_usage"] == 'light' or i["last_usage"] == 'window' or i["last_usage"] == 'windowFrench' or i["last_usage"] == 'belmDoor':
                # print('{} {}'.format(i["id_endpoint"],i["name"]))
                # device_name[i["id_endpoint"]] = i["name"]
                device_name[i["id_device"]] = i["name"]
                device_type[i["id_device"]] = i["last_usage"]
                device_endpoint[i["id_device"]] = i["id_endpoint"]

            if i["last_usage"] == 'alarm':
                # print('{} {}'.format(i["id_endpoint"], i["name"]))
                device_name[i["id_endpoint"]] = "Tyxal Alarm"
                device_type[i["id_device"]] = 'alarm'
                device_endpoint[i["id_device"]] = i["id_endpoint"]
        print('Configuration updated')
        
    async def parse_devices_data(self, parsed):
        for i in parsed:
            if i["endpoints"][0]["error"] == 0:
                try:
                    attr_alarm = {}
                    attr_alarm_details = {}
                    attr_cover = {}
                    attr_cover_details = {}
                    attr_door ={}
                    attr_window ={}
                    attr_light = {}
                    attr_light_details = {}
                    device_id = i["id"]
                    name_of_id = self.get_name_from_id(device_id)
                    type_of_id = self.get_type_from_id(device_id)
                    
                    _LOGGER.debug("======[ DEVICE INFOS ]======")
                    _LOGGER.debug("ID {}".format(device_id))
                    _LOGGER.debug("Name {}".format(name_of_id))
                    _LOGGER.debug("Type {}".format(type_of_id))
                    _LOGGER.debug("==========================")
                    
                    for elem in i["endpoints"][0]["data"]:
                        _LOGGER.debug("CURRENT ELEM={}".format(elem))
                        endpoint_id = None

                        elementName = None
                        elementValue = None
                        elementValidity = None

                        # Get full name of this id
                        # endpoint_id = i["endpoints"][0]["id"]

                        # Element name
                        elementName = elem["name"]
                        # Element value
                        elementValue = elem["value"]
                        elementValidity = elem["validity"]
                        print_id = None


                        if len(name_of_id) != 0:
                            print_id = name_of_id
                            endpoint_id = device_endpoint[device_id]
                        else:
                            print_id = device_id
                            endpoint_id = device_endpoint[device_id]

                        if type_of_id == 'light':
                            if elementName in deviceLightKeywords and elementValidity == 'upToDate':  # NEW METHOD
                                _LOGGER.debug('ITS A LIGHT!')
                                attr_light['device_id'] = device_id
                                attr_light['endpoint_id'] = endpoint_id
                                attr_light['id'] = str(device_id) + '_' + str(endpoint_id)
                                attr_light['light_name'] = print_id
                                attr_light['name'] = print_id
                                attr_light['device_type'] = 'light'
                                attr_light[elementName] = elementValue

                                # if elementName in deviceCoverDetailsKeywords:
                                #     attr_cover_details[elementName] = elementValue
                                # else:
                                #     attr_cover[elementName] = elementValue
                                # attr_cover['attributes'] = attr_cover_details
                        if type_of_id == 'shutter':
                            if elementName in deviceCoverKeywords and elementValidity == 'upToDate': #NEW METHOD
                                _LOGGER.debug('ITS A SHUTTER!')
                                attr_cover['device_id'] = device_id
                                attr_cover['endpoint_id'] = endpoint_id
                                attr_cover['id'] = str(device_id)+'_'+str(endpoint_id)
                                attr_cover['cover_name'] = print_id
                                attr_cover['name'] = print_id
                                attr_cover['device_type'] = 'cover'
                                attr_cover[elementName] = elementValue

                            # if elementName in deviceCoverDetailsKeywords:
                            #     attr_cover_details[elementName] = elementValue
                            # else:
                            #     attr_cover[elementName] = elementValue
                            # attr_cover['attributes'] = attr_cover_details

                        if type_of_id == 'belmDoor':
                            if elementName in deviceDoorKeywords and elementValidity == 'upToDate': #NEW METHOD
                                _LOGGER.debug('ITS A DOOR!')
                                attr_door['device_id'] = device_id
                                attr_door['endpoint_id'] = endpoint_id
                                attr_door['id'] = str(device_id)+'_'+str(endpoint_id)
                                attr_door['door_name'] = print_id
                                attr_door['name'] = print_id
                                attr_door['device_type'] = 'sensor'
                                attr_door[elementName] = elementValue

                        if type_of_id == 'windowFrench' or type_of_id == 'window':
                            if elementName in deviceDoorKeywords and elementValidity == 'upToDate': #NEW METHOD
                                _LOGGER.debug('ITS A WINDOW!')
                                attr_window['device_id'] = device_id
                                attr_window['endpoint_id'] = endpoint_id
                                attr_window['id'] = str(device_id)+'_'+str(endpoint_id)
                                attr_window['door_name'] = print_id
                                attr_window['name'] = print_id
                                attr_window['device_type'] = 'sensor'
                                attr_window[elementName] = elementValue

                        if type_of_id == 'alarm':
                            if elementName in deviceAlarmKeywords and elementValidity == 'upToDate':
                                _LOGGER.debug('ITS AN ALARM!')
                                attr_alarm['device_id'] = device_id
                                attr_alarm['endpoint_id'] = endpoint_id
                                attr_alarm['id'] = str(device_id)+'_'+str(endpoint_id)
                                attr_alarm['alarm_name']="Tyxal Alarm"
                                attr_alarm['name']="Tyxal Alarm"
                                attr_alarm['device_type'] = 'alarm_control_panel'
                                attr_alarm[elementName] = elementValue
                                # if elementName in deviceAlarmDetailsKeywords:
                                #     attr_alarm_details[elementName] = elementValue
                                # else:
                                #     attr_alarm[elementName] = elementValue
                                # attr_alarm['attributes'] = attr_alarm_details #KEEPING original details for attributes
                                # print(attr_alarm['attributes'])

                except Exception as e:
                    print('msg_data error in parsing !')
                    print(e)

                if 'device_type' in attr_cover and attr_cover['device_type'] == 'cover':
                    # print(attr_cover)
                    new_cover = "cover_tydom_"+str(endpoint_id)
                    new_cover = Cover(tydom_attributes=attr_cover, mqtt=self.mqtt_client) #NEW METHOD
                    # new_cover = Cover(id=endpoint_id,name=print_id, current_position=elementValue, attributes=i, mqtt=self.mqtt_client)
                    await new_cover.update()
                elif 'device_type' in attr_door and attr_door['device_type'] == 'sensor':
                    # print(attr_cover)
                    new_door = "door_tydom_"+str(endpoint_id)
                    new_door = sensor(elem_name='openState', tydom_attributes_payload=attr_door, attributes_topic_from_device='useless', mqtt=self.mqtt_client)
                    # new_cover = Cover(id=endpoint_id,name=print_id, current_position=elementValue, attributes=i, mqtt=self.mqtt_client)
                    await new_door.update()
                elif 'device_type' in attr_window and attr_window['device_type'] == 'sensor':
                    # print(attr_cover)
                    new_window = "window_tydom_"+str(endpoint_id)
                    new_window = sensor(elem_name='openState', tydom_attributes_payload=attr_window, attributes_topic_from_device='useless', mqtt=self.mqtt_client)
                    # new_cover = Cover(id=endpoint_id,name=print_id, current_position=elementValue, attributes=i, mqtt=self.mqtt_client)
                    await new_window.update()
                elif 'device_type' in attr_light and attr_light['device_type'] == 'light':
                    # print(attr_cover)
                    new_light = "light_tydom_"+str(endpoint_id)
                    new_light = Light(tydom_attributes=attr_light, mqtt=self.mqtt_client) #NEW METHOD
                    # new_cover = Cover(id=endpoint_id,name=print_id, current_position=elementValue, attributes=i, mqtt=self.mqtt_client)
                    await new_light.update()
                # Get last known state (for alarm) # NEW METHOD
                elif 'device_type' in attr_alarm and attr_alarm['device_type'] == 'alarm_control_panel':
                    # print(attr_alarm)
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

                        if 'alarmSOS' in attr_alarm and attr_alarm['alarmSOS'] == "true":
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
                            alarm = Alarm(current_state=state, tydom_attributes=attr_alarm, mqtt=self.mqtt_client)
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

    def get_type_from_id(self, id):
        return(device_type[id])

    # Get pretty name for a device id
    def get_name_from_id(self, id):
        name = ""
        if len(device_name) != 0:
            name = device_name[id]
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


