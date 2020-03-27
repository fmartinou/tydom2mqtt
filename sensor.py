import json
import time
from datetime import datetime

sensor_topic = "sensor/tydom/#"
sensor_config_topic = "homeassistant/sensor/tydom/{id}/config"
sensor_state_topic = "sensor/tydom/{id}/state"
sensor_attributes_topic = "sensor/tydom/{id}/attributes"

class sensor:

    def __init__(self, state_id, tydom_attributes=None, mqtt=None):
        self.attributes = tydom_attributes
        
        self.id = self.attributes['id']
        self.name = self.attributes['sensor_name']
        self.state = self.attributes[state_id]
        self.mqtt = mqtt

    async def setup(self):
        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'Sensor'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id

        self.config_sensor_topic = sensor_config_topic.format(id=self.id)

        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        self.config['device'] = self.device
        # self.config['attributes'] = self.attributes
        self.config['state_topic'] = sensor_state_topic.format(id=self.id)
        self.config['json_attributes_topic'] = sensor_attributes_topic.format(id=self.id)

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_sensor_topic, json.dumps(self.config), qos=0) #sensor Config


    async def update(self):
        await self.setup()
        self.state_topic = sensor_state_topic.format(id=self.id, state=self.state)
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.state_topic, self.state, qos=0, retain=True) #sensor State
            self.mqtt.mqtt_client.publish(self.config['json_attributes_topic'], self.attributes, qos=0)

        print("Sensor created / updated : ", self.name, self.id, self.state)
