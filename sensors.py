import json
import time
from datetime import datetime

sensor_topic = "sensor/tydom/#"
sensor_config_topic = "homeassistant/sensor/tydom/{id}/config"

binary_sensor_topic = "binary_sensor/tydom/#"
binary_sensor_config_topic = "homeassistant/binary_sensor/tydom/{id}/config"

# sensor_state_topic = "sensor/tydom/{id}/state"
# State topic can be the same as the original device attributes topic !
class sensor:

    def __init__(self, elem_name, tydom_attributes_payload, attributes_topic_from_device, mqtt=None):
        self.attributes = tydom_attributes_payload

        self.sensor_state_topic = attributes_topic_from_device
        self.id = elem_name+'_tydom_'+str(self.attributes['id'])
        self.name = elem_name+'_tydom_'+str(self.attributes['id'])+'_'+self.attributes['device_type']
        
        self.elem_name = elem_name
        
        # print(self.elem_name)
        # print(self.attributes[self.elem_name])
        self.mqtt = mqtt
        self.elem_value = self.attributes[self.elem_name]


        self.binary = False
        self.config_topic = sensor_config_topic.format(id=self.id)
        if self.elem_value == False or self.elem_value == True:
            self.binary = True
            self.config_topic = binary_sensor_config_topic.format(id=self.id)
        else:
            self.config_topic = sensor_config_topic.format(id=self.id)

        self.device_class = 'problem'
        if 'emperature' in self.elem_name:
            self.device_class = 'temperature'
        elif 'efect' in self.elem_name:
            self.device_class = 'problem'
        elif 'ntrusion' in self.elem_name or 'zone' in self.elem_name or 'alarm' in self.elem_name:
            self.device_class = 'safety'
        elif 'gsm' in self.elem_name:
            self.device_class = 'signal_strength'


    # SENSOR:
    # None: Generic sensor. This is the default and doesn’t need to be set.
    # battery: Percentage of battery that is left.
    # humidity: Percentage of humidity in the air.
    # illuminance: The current light level in lx or lm.
    # signal_strength: Signal strength in dB or dBm.
    # temperature: Temperature in °C or °F.
    # power: Power in W or kW.
    # pressure: Pressure in hPa or mbar.
    # timestamp: Datetime object or timestamp string.        
    # BINARY :
    # None: Generic on/off. This is the default and doesn’t need to be set.
    # battery: on means low, off means normal
    # cold: on means cold, off means normal
    # connectivity: on means connected, off means disconnected
    # door: on means open, off means closed
    # garage_door: on means open, off means closed
    # gas: on means gas detected, off means no gas (clear)
    # heat: on means hot, off means normal
    # light: on means light detected, off means no light
    # lock: on means open (unlocked), off means closed (locked)
    # moisture: on means moisture detected (wet), off means no moisture (dry)
    # motion: on means motion detected, off means no motion (clear)
    # moving: on means moving, off means not moving (stopped)
    # occupancy: on means occupied, off means not occupied (clear)
    # opening: on means open, off means closed
    # plug: on means device is plugged in, off means device is unplugged
    # power: on means power detected, off means no power
    # presence: on means home, off means away
    # problem: on means problem detected, off means no problem (OK)
    # safety: on means unsafe, off means safe
    # smoke: on means smoke detected, off means no smoke (clear)
    # sound: on means sound detected, off means no sound (clear)
    # vibration: on means vibration detected, off means no vibration (clear)
    # window: on means open, off means closed

    async def setup(self):
        # self.device = {}
        # self.device['manufacturer'] = 'Delta Dore'
        # self.device['model'] = 'Sensor'
        # self.device['name'] = self.name
        # self.device['identifiers'] = self.id

        self.config_sensor_topic = sensor_config_topic.format(id=self.id)

        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        self.config['device_class'] = self.device_class
        self.config['value_template'] = "{{ value_json."+self.elem_name+" }}"
        # self.config['device'] = self.device
        # self.config['attributes'] = self.attributes
        self.config['state_topic'] = self.sensor_state_topic

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_topic, json.dumps(self.config), qos=0) #sensor Config


    async def update(self):

        # 3 items or necessary :
            # config to config config_sensor_topic + config payload is the schema
            # state payload to state topic in config with all attributes


        await self.setup()

        # self.state_topic = sensor_state_topic.format(id=self.id, state=self.attributes)
        # if (self.mqtt != None):
        #     self.mqtt.mqtt_client.publish(self.sensor_state_topic, self.attributes, qos=0, retain=True) #sensor State
            # self.mqtt.mqtt_client.publish(self.config['json_attributes_topic'], self.attributes, qos=0)
        if self.binary == False:
            print("Sensor created / updated : ", self.name)
        else:
            print("Binary sensor created / updated : ", self.name)