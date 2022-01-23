import json
import time
from datetime import datetime
from sensors import sensor
from logger import logger
import logging

logger = logging.getLogger(__name__)
alarm_topic = "alarm_control_panel/tydom/#"
alarm_config_topic = "homeassistant/alarm_control_panel/tydom/{id}/config"
alarm_state_topic = "alarm_control_panel/tydom/{id}/state"
alarm_command_topic = "alarm_control_panel/tydom/{id}/set_alarm_state"
alarm_attributes_topic = "alarm_control_panel/tydom/{id}/attributes"


class Alarm:

    def __init__(self, current_state, alarm_pin=None,
                 tydom_attributes=None, mqtt=None):
        self.attributes = tydom_attributes
        self.device_id = self.attributes['device_id']
        self.endpoint_id = self.attributes['endpoint_id']
        self.id = self.attributes['id']
        self.name = self.attributes['name']
        self.current_state = current_state
        self.mqtt = mqtt
        self.alarm_pin = alarm_pin

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
        #self.config['code'] = self.alarm_pin

        self.config['code_arm_required'] = 'false'

        if (self.alarm_pin is None):
            self.config['code'] = self.alarm_pin
            self.config['code_arm_required'] = 'true'

        self.config['json_attributes_topic'] = alarm_attributes_topic.format(
            id=self.id)

        if (self.mqtt is not None):
            self.mqtt.mqtt_client.publish(
                self.config_alarm_topic, json.dumps(
                    self.config), qos=0)  # Alarm Config

    async def update(self):
        await self.setup()

        try:
            await self.update_sensors()
        except Exception as e:
            logger.error("Alarm sensors Error :")
            logger.error(e)

        self.state_topic = alarm_state_topic.format(
            id=self.id, state=self.current_state)
        if (self.mqtt is not None):
            self.mqtt.mqtt_client.publish(
                self.state_topic,
                self.current_state,
                qos=0,
                retain=True)  # Alarm State
            self.mqtt.mqtt_client.publish(
                self.config['json_attributes_topic'], self.attributes, qos=0)
        logger.info(
            "Alarm created / updated : %s %s %s",
            self.name,
            self.id,
            self.current_state)

    async def update_sensors(self):
        # logger.info('test sensors !')
        for i, j in self.attributes.items():
            # if j == 'ON' and not 'alarm' in i:
            #     j = True
            # elif j == 'OFF' and not 'alarm' in i:
            #     j == False
            # sensor_name = "tydom_alarm_sensor_"+i
            # logger.debug("name %s elem_name %s attributes_topic_from_device %s mqtt %s", sensor_name, i, self.config['json_attributes_topic'], self.mqtt)
            if not i == 'device_type' or not i == 'id':
                new_sensor = None
                new_sensor = sensor(
                    elem_name=i,
                    tydom_attributes_payload=self.attributes,
                    attributes_topic_from_device=self.config['json_attributes_topic'],
                    mqtt=self.mqtt)
                await new_sensor.update()
    # def __init__(self, name, elem_name, tydom_attributes_payload,
    # attributes_topic_from_device, mqtt=None):

    async def put_alarm_state(self, tydom_client, device_id, alarm_id, home_zone, night_zone, asked_state=None):
        # logger.debug("%s %s %s %s", tydom_client, device_id, alarm_id, asked_state)

        value = None
        zone_id = None

        if asked_state == 'ARM_AWAY':
            value = 'ON'
            zone_id = None
        elif asked_state == 'ARM_HOME':  # TODO : Separate both and let user specify with zone is what
            value = "ON"
            zone_id = home_zone
        elif asked_state == 'ARM_NIGHT':  # TODO : Separate both and let user specify with zone is what
            value = "ON"
            zone_id = night_zone
        elif asked_state == 'DISARM':
            value = 'OFF'
            zone_id = None

        await tydom_client.put_alarm_cdata(device_id=device_id, alarm_id=alarm_id, value=value, zone_id=zone_id)
