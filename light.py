import json
import time
from datetime import datetime
from sensors import sensor
from logger import logger
import logging

logger = logging.getLogger(__name__)
light_command_topic = "light/tydom/{id}/set_levelCmd"
light_config_topic = "homeassistant/light/tydom/{id}/config"
light_level_topic = "light/tydom/{id}/current_level"
light_set_level_topic = "light/tydom/{id}/set_level"
light_attributes_topic = "light/tydom/{id}/attributes"


class Light:
    def __init__(self, tydom_attributes, set_level=None, mqtt=None):

        self.attributes = tydom_attributes
        self.device_id = self.attributes['device_id']
        self.endpoint_id = self.attributes['endpoint_id']
        self.id = self.attributes['id']
        self.name = self.attributes['light_name']
        try:
            self.current_level = self.attributes['level']
        except Exception as e:
            logger.error(e)
            self.current_level = None
        self.set_level = set_level
        self.mqtt = mqtt

    # def id(self):
    #     return self.id

    # def name(self):
    #     return self.name

    # def current_level(self):
    #     return self.current_level

    # def set_level(self):
    #     return self.set_level

    # def attributes(self):
    #     return self.attributes

    async def setup(self):
        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'Lumiere'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id

        self.config_topic = light_config_topic.format(id=self.id)
        self.config = {}
        self.config['name'] = self.name
        self.config['brightness_scale'] = 100
        self.config['unique_id'] = self.id
        self.config['optimistic'] = True
        self.config['brightness_state_topic'] = light_level_topic.format(
            id=self.id)
        self.config['brightness_command_topic'] = light_set_level_topic.format(
            id=self.id)
        self.config['command_topic'] = light_command_topic.format(id=self.id)
        # self.config['set_level_topic'] = light_set_level_topic.format(id=self.id)
        self.config['state_topic'] = light_level_topic.format(id=self.id)
        self.config['json_attributes_topic'] = light_attributes_topic.format(
            id=self.id)

        self.config['payload_on'] = "ON"
        self.config['payload_on'] = "ON"
        self.config['on_command_type'] = "brightness"
        self.config['retain'] = 'false'
        self.config['device'] = self.device
        # logger.debug(self.config)

        if (self.mqtt is not None):
            self.mqtt.mqtt_client.publish(
                self.config_topic, json.dumps(
                    self.config), qos=0)
        # setup_pub = '(self.config_topic, json.dumps(self.config), qos=0)'
        # return(setup_pub)

    async def update(self):
        await self.setup()

        try:
            await self.update_sensors()
        except Exception as e:
            logger.error("light sensors Error :")
            logger.error(e)

        self.level_topic = light_level_topic.format(
            id=self.id, current_level=self.current_level)

        if (self.mqtt is not None):
            self.mqtt.mqtt_client.publish(
                self.level_topic, self.current_level, qos=0, retain=True)
            # self.mqtt.mqtt_client.publish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
            self.mqtt.mqtt_client.publish(
                self.config['json_attributes_topic'], self.attributes, qos=0)
        logger.info(
            "light created / updated : %s %s %s",
            self.name,
            self.id,
            self.current_level)

        # update_pub = '(self.level_topic, self.current_level, qos=0, retain=True)'
        # return(update_pub)

    async def update_sensors(self):
        # logger.info('test sensors !')
        for i, j in self.attributes.items():
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

    @staticmethod
    async def put_level(tydom_client, device_id, light_id, level):
        logger.info("%s %s %s", light_id, 'level', level)
        if not (level == ''):
            await tydom_client.put_devices_data(device_id, light_id, 'level', level)

    @staticmethod
    async def put_level_cmd(tydom_client, device_id, light_id, level_cmd):
        logger.info("%s %s %s", light_id, 'levelCmd', level_cmd)
        if not (level_cmd == ''):
            await tydom_client.put_devices_data(device_id, light_id, 'levelCmd', level_cmd)
