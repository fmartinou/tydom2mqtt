import json
import time
from datetime import datetime

alarm_topic = "alarm_control_panel/tydom/#"
alarm_config_topic = "homeassistant/alarm_control_panel/tydom/{id}/config"
alarm_state_topic = "alarm_control_panel/tydom/{id}/state"
alarm_command_topic = "alarm_control_panel/tydom/{id}/set_alarm_state"
alarm_attributes_topic = "alarm_control_panel/tydom/{id}/attributes"

class Alarm:

    def __init__(self, id, name, current_state=None, attributes=None, mqtt=None):
        self.id = id
        self.name = name
        self.current_state = current_state
        self.attributes = attributes
        self.mqtt = mqtt

    async def setup(self):
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
        # self.config['attributes'] = self.attributes
        self.config['command_topic'] = alarm_command_topic.format(id=self.id)
        self.config['state_topic'] = alarm_state_topic.format(id=self.id)
        self.config['code_arm_required'] = 'false'

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_alarm_topic, json.dumps(self.config), qos=0) #Alarm Config


    async def update(self):
        await self.setup()
        self.state_topic = alarm_state_topic.format(id=self.id, state=self.current_state)
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.state_topic, self.current_state, qos=0, retain=True) #Alarm State

        print("Alarm created / updated : ", self.name, self.id, self.current_state)

    async def put_alarm_state(tydom_client, alarm_id, asked_state=None):
        print(tydom_client, alarm_id, asked_state)

        state = None
        zone = None
        if asked_state == 'ARM_AWAY':
            state = 'ON'
            zone = None
        elif asked_state == 'ARM_HOME' or asked_state == 'ARM_NIGHT': #TODO : Separate both and let user specify with zone is what
            state = "ON"
            zone = "zone1"
        elif asked_state == 'DISARM':
            state = 'OFF'
            zone = None

        await tydom_client.put_alarm_cdata(alarm_id=alarm_id, asked_state=state, zone=zone)

        # update_pub = '(self.state_topic, self.current_state, qos=0, retain=True)'
        # return(update_pub)
        # self.attributes_topic = alarm_attributes_topic.format(id=self.id, attributes=self.attributes)
        # hassio.publish(self.attributes_topic, self.attributes, qos=0)

## if (!pin) {
      #   callback(null);
      #   return;
      # }
      # if ([SecuritySystemTargetState.AWAY_ARM, SecuritySystemTargetState.DISARM].includes(value as number)) {
      #   const nextValue = value === SecuritySystemTargetState.DISARM ? 'OFF' : 'ON';
      #   await client.put(`/devices/${deviceId}/endpoints/${endpointId}/cdata?name=alarmCmd`, {
      #     value: nextValue,
      #     pwd: pin
      #   });
      #   debugSetResult('SecuritySystemTargetState', {name, id, value: nextValue});
      # }
      # if ([SecuritySystemTargetState.STAY_ARM, SecuritySystemTargetState.NIGHT_ARM].includes(value as number)) {
      #   const nextValue = value === SecuritySystemTargetState.DISARM ? 'OFF' : 'ON';
      #   const targetZones = value === SecuritySystemTargetState.STAY_ARM ? aliases.stay : aliases.night;
      #   if (Array.isArray(targetZones) && targetZones.length > 0) {
      #     await client.put(`/devices/${deviceId}/endpoints/${endpointId}/cdata?name=zoneCmd`, {
      #       value: nextValue,
      #       pwd: pin,
      #       zones: targetZones
      #     });
      #   }
        
        

