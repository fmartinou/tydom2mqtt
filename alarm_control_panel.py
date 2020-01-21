import json
import time
from datetime import datetime

alarm_topic = "alarm_control_panel/tydom/#"
alarm_config = "homeassistant/alarm_control_panel/tydom/{id}/config"
alarm_state_topic = "alarm_control_panel/tydom/{id}/state"
alarm_command_topic = "alarm_control_panel/tydom/{id}/set"
alarm_sos_topic = "binary_sensor/tydom/{id}/sos"
alarm_attributes_topic = "alarm_control_panel/tydom/{id}/attributes"


class Alarm:

    def __init__(self, id, name, current_state=None, attributes=None, mqtt=None):
        self.id = id
        self.name = name
        self.current_state = current_state
        self.attributes = attributes
        self.mqtt = mqtt

    def setup(self):
        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'Tyxal'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id
        self.config_alarm = alarm_config.format(id=self.id)
        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        self.config['device'] = self.device
        # self.config['attributes'] = self.attributes
        self.config['command_topic'] = alarm_command_topic.format(id=self.id)
        self.config['state_topic'] = alarm_state_topic.format(id=self.id)


        # print(self.config)
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_alarm, json.dumps(self.config), qos=0)
        # config_pub = '(self.config_alarm, json.dumps(self.config), qos=0)'
        # return(config_pub)

    def update(self):
        self.setup()
        self.state_topic = alarm_state_topic.format(id=self.id, state=self.current_state)
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.state_topic, self.current_state, qos=0, retain=True)
            self.mqtt.mqtt_client.publish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)

        # update_pub = '(self.state_topic, self.current_state, qos=0, retain=True)'
        # return(update_pub)
        # self.attributes_topic = alarm_attributes_topic.format(id=self.id, attributes=self.attributes)
        # hassio.publish(self.attributes_topic, self.attributes, qos=0)
 
