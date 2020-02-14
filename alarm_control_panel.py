import json
import time
from datetime import datetime

alarm_topic = "alarm_control_panel/tydom/#"
alarm_config_topic = "homeassistant/alarm_control_panel/tydom/{id}/config"
alarm_state_topic = "alarm_control_panel/tydom/{id}/state"
alarm_command_topic = "alarm_control_panel/tydom/{id}/set"
alarm_sos_config_topic = "homeassistant/binary_sensor/tydom/{id}/config"
alarm_sos_state_topic = "binary_sensor/tydom/{id}/state"
alarm_attributes_topic = "alarm_control_panel/tydom/{id}/attributes"

class Alarm:

    def __init__(self, id, name, current_state=None, sos=None, attributes=None, mqtt=None, out_temp=None):
        self.id = id
        self.name = name
        self.current_state = current_state
        self.attributes = attributes
        self.sos = sos
        self.mqtt = mqtt
        self.out_temp = out_temp

    def setup(self):
        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'Tyxal'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id

        self.config_alarm_topic = alarm_config_topic.format(id=self.id)

        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        self.config['device'] = self.device
        self.config['attributes'] = self.attributes
        self.config['command_topic'] = alarm_command_topic.format(id=self.id)
        self.config['state_topic'] = alarm_state_topic.format(id=self.id)
        self.config['code_arm_required'] = 'false'

        ### SOS binary sensor
        self.sos_device = {}
        self.sos_device['manufacturer'] = 'Delta Dore'
        self.sos_device['model'] = 'Tyxal'
        self.sos_device['name'] = 'SOS Tyxal'
        self.sos_device['identifiers'] = self.id
        self.sos_device['device_class'] = 'problem'

        self.config_sos_topic = alarm_sos_config_topic.format(id=self.sos_device['identifiers'])

        self.sos_config = {}
        self.sos_config['name'] = self.sos_device['name']
        self.sos_config['unique_id'] =  self.sos_device['identifiers']
        self.sos_config['device'] = self.sos_device
        self.sos_config['state_topic'] = alarm_sos_state_topic.format(id=self.sos_config['unique_id'])

        # print(self.config)
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_alarm_topic, json.dumps(self.config), qos=0) #Alarm Config
            self.mqtt.mqtt_client.publish(self.config_sos_topic, json.dumps(self.sos_config), qos=0) #SOS Config
        # config_pub = '(self.config_alarm_topic, json.dumps(self.config), qos=0)'
        # return(config_pub)

    def update(self):
        self.setup()
        self.state_topic = alarm_state_topic.format(id=self.id, state=self.current_state)
        self.sos_state_topic = alarm_sos_state_topic.format(id=self.sos_device['identifiers'], state=self.sos)
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.state_topic, self.current_state, qos=0, retain=True) #Alarm State
            self.mqtt.mqtt_client.publish(self.sos_state_topic, self.sos, qos=0, retain=True) #SOS State

            self.mqtt.mqtt_client.publish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
        print("Alarm created / updated : ", self.name, self.id, self.current_state, self.sos, self.out_temp)




        # update_pub = '(self.state_topic, self.current_state, qos=0, retain=True)'
        # return(update_pub)
        # self.attributes_topic = alarm_attributes_topic.format(id=self.id, attributes=self.attributes)
        # hassio.publish(self.attributes_topic, self.attributes, qos=0)
 
