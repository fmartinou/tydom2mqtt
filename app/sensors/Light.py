import json
import logging
from .Sensor import Sensor

logger = logging.getLogger(__name__)
light_command_topic = "light/tydom/{id}/set_levelCmd"
light_config_topic = "homeassistant/light/tydom/{id}/config"
light_level_topic = "light/tydom/{id}/current_level"
light_set_level_topic = "light/tydom/{id}/set_level"
light_attributes_topic = "light/tydom/{id}/attributes"


class Light:
    def __init__(self, tydom_attributes, set_level=None, mqtt=None):
        self.level_topic = None
        self.config_topic = None
        self.config = None
        self.device = None
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

    async def setup(self):
        self.device = {
            'manufacturer': 'Delta Dore',
            'model': 'Lumiere',
            'name': self.name,
            'identifiers': self.id}
        self.config_topic = light_config_topic.format(id=self.id)
        self.config = {
            'name': self.name,
            'brightness_scale': 100,
            'unique_id': self.id,
            'optimistic': True,
            'brightness_state_topic': light_level_topic.format(
                id=self.id),
            'brightness_command_topic': light_set_level_topic.format(
                id=self.id),
            'command_topic': light_command_topic.format(
                id=self.id),
            'state_topic': light_level_topic.format(
                id=self.id),
            'json_attributes_topic': light_attributes_topic.format(
                id=self.id),
            'payload_on': "ON",
            'on_command_type': "brightness",
            'retain': 'false',
            'device': self.device}

        if self.mqtt is not None:
            self.mqtt.mqtt_client.publish(
                self.config_topic, json.dumps(
                    self.config), qos=0, retain=True)

    async def update(self):
        await self.setup()

        try:
            await self.update_sensors()
        except Exception as e:
            logger.error("light sensors Error :")
            logger.error(e)

        self.level_topic = light_level_topic.format(
            id=self.id, current_level=self.current_level)

        if self.mqtt is not None:
            self.mqtt.mqtt_client.publish(
                self.level_topic, self.current_level, qos=0, retain=True)
            self.mqtt.mqtt_client.publish(
                self.config['json_attributes_topic'], self.attributes, qos=0, retain=True)
        logger.info(
            "light created / updated : %s %s %s",
            self.name,
            self.id,
            self.current_level)

    async def update_sensors(self):
        for i, j in self.attributes.items():
            if not i == 'device_type' or not i == 'id':
                new_sensor = Sensor(
                    elem_name=i,
                    tydom_attributes_payload=self.attributes,
                    mqtt=self.mqtt)
                await new_sensor.update()

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
