import json
import time
from datetime import datetime
from sensors import sensor

climate_config_topic = "homeassistant/climate/tydom/{id}/config"
sensor_config_topic = "homeassistant/sensor/tydom/{id}/config"
climate_json_attributes_topic = "climate/tydom/{id}/state"

temperature_command_topic = "climate/tydom/{id}/set_setpoint"
temperature_state_topic = "climate/tydom/{id}/setpoint"
current_temperature_topic = "climate/tydom/{id}/temperature"
mode_state_topic = "climate/tydom/{id}/hvacMode"
mode_command_topic = "climate/tydom/{id}/set_hvacMode"
swing_mode_state_topic = "climate/tydom/{id}/thermicLevel"
swing_mode_command_topic = "climate/tydom/{id}/set_thermicLevel"
out_temperature_state_topic = "sensor/tydom/{id}/temperature"

#temperature = current_temperature_topic 
#setpoint= temperature_command_topic
#temperature_unit=C
#"modes": ["STOP", "ANTI-FROST","ECO", "COMFORT"],
#####################################
#setpoint (seulement si thermostat)
#temperature (intérieure, seulement si thermostat)
#anticipCoeff 30 (seulement si thermostat)

#thermicLevel STOP ECO ...
#auhorisation HEATING
#hvacMode NORMAL None (si off)
#timeDelay : 0
#tempoOn : False
#antifrost True False
#openingdetected False
#presenceDetected False
#absence False
#LoadSheddingOn False

#outTemperature float
##################################

# climate_json_attributes_topic = "climate/tydom/{id}/state"
# State topic can be the same as the original device attributes topic !
class Boiler:

    def __init__(self, tydom_attributes, tydom_client=None, mqtt=None):
        
        self.attributes = tydom_attributes
        self.device_id = self.attributes['device_id']
        self.endpoint_id = self.attributes['endpoint_id']
        self.id = self.attributes['id']
        self.name = self.attributes['name']
        self.mqtt = mqtt
        self.tydom_client = tydom_client

    async def setup(self):
        self.device = {}
        self.config = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id
        # Check if device is an outer temperature sensor
        if 'outTemperature' in self.attributes:
            self.config['name'] = 'Out Temperature'
            self.device['model'] = 'Sensor'
            self.config['device_class'] = 'temperature'
            self.config['unit_of_measurement'] = 'C'
            self.config_topic = sensor_config_topic.format(id=self.id)
            self.config['state_topic'] = out_temperature_state_topic.format(id=self.id)
            self.topic_to_func = {}
        # Check if device is a heater with thermostat sensor
        else:
#        elif 'setpoint' in self.attributes:
            self.config['name'] = self.name
            self.device['model'] = 'Climate'
            self.config_topic = climate_config_topic.format(id=self.id)
            self.config['temperature_command_topic'] = temperature_command_topic.format(id=self.id)
            self.config['temperature_state_topic'] = temperature_state_topic.format(id=self.id)
            self.config['current_temperature_topic'] = current_temperature_topic.format(id=self.id)
            self.config['modes'] = ["off", "heat"]
            self.config['mode_state_topic'] = mode_state_topic.format(id=self.id)
            self.config['mode_command_topic'] = mode_command_topic.format(id=self.id)
            self.config['swing_modes'] = ["STOP","ANTI_FROST","ECO","COMFORT"]
            self.config['swing_mode_state_topic'] = swing_mode_state_topic.format(id=self.id)
            self.config['swing_mode_command_topic'] = swing_mode_command_topic.format(id=self.id)
        # Electrical heater without thermostat
#        else:
#            self.boilertype = 'Electrical'
#            self.config['name'] = self.name
#            self.device['model'] = 'Climate'
#            self.config_topic = climate_config_topic.format(id=self.id)
#            self.config['modes'] = ["off", "heat"]
#            self.config['mode_state_topic'] = mode_state_topic.format(id=self.id)
#            self.config['mode_command_topic'] = mode_command_topic.format(id=self.id)
#            self.config['swing_modes'] = ["STOP","ANTI-FROST","ECO","COMFORT"]
#            self.config['swing_mode_state_topic'] = swing_mode_state_topic.format(id=self.id)
#            self.config['swing_mode_command_topic'] = swing_mode_command_topic.format(id=self.id)

        self.config['unique_id'] = self.id

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_topic, json.dumps(self.config), qos=0)

    async def update(self):
        await self.setup()
        
        if (self.mqtt != None):
            if 'temperature' in self.attributes and self.attributes['temperature'] != 'None':
                self.mqtt.mqtt_client.publish(self.config['current_temperature_topic'], self.attributes['temperature'], qos=0)
            if 'setpoint' in self.attributes:
                if self.attributes['setpoint'] != 'None':
#                    self.mqtt.mqtt_client.publish(self.config['temperature_command_topic'], self.attributes['setpoint'], qos=0)
                    self.mqtt.mqtt_client.publish(self.config['temperature_state_topic'], self.attributes['setpoint'], qos=0)
                else:
                    self.mqtt.mqtt_client.publish(self.config['temperature_state_topic'], '10', qos=0)
#            if 'hvacMode' in self.attributes:
#                self.mqtt.mqtt_client.publish(self.config['mode_state_topic'], "heat" if self.attributes['hvacMode'] == "NORMAL" else "off", qos=0)
#            if 'authorization' in self.attributes:
#                self.mqtt.mqtt_client.publish(self.config['mode_state_topic'], "off" if self.attributes['authorization'] == "STOP" else "heat", qos=0)
            if 'thermicLevel' in self.attributes:
                self.mqtt.mqtt_client.publish(self.config['mode_state_topic'], "off" if self.attributes['thermicLevel'] == "STOP" else "heat", qos=0)
                self.mqtt.mqtt_client.publish(self.config['swing_mode_state_topic'], self.attributes['thermicLevel'], qos=0)
            if 'outTemperature' in self.attributes:
                self.mqtt.mqtt_client.publish(self.config['state_topic'], self.attributes['outTemperature'], qos=0)

        # print("Boiler created / updated : ", self.name, self.id, self.current_position)       

    async def put_temperature(tydom_client, device_id, boiler_id, set_setpoint):
        print(boiler_id, 'set_setpoint', set_setpoint)
        if not (set_setpoint == ''):
            await tydom_client.put_devices_data(device_id, boiler_id, 'setpoint', set_setpoint) 		

    async def put_hvacMode(tydom_client, device_id, boiler_id, set_hvacMode):
        print(boiler_id, 'set_hvacMode', set_hvacMode)
        if set_hvacMode == 'off':
            await tydom_client.put_devices_data(device_id, boiler_id, 'thermicLevel', 'STOP')
        else:
            await tydom_client.put_devices_data(device_id, boiler_id, 'thermicLevel', 'COMFORT')
            await tydom_client.put_devices_data(device_id, boiler_id, 'setpoint', '10')

    async def put_thermicLevel(tydom_client, device_id, boiler_id, set_thermicLevel):
        print(boiler_id, 'thermicLevel', set_thermicLevel)
        if not (set_thermicLevel == ''):
            await tydom_client.put_devices_data(device_id, boiler_id, 'thermicLevel', set_thermicLevel)