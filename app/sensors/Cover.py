import json
import logging
from .Sensor import Sensor

logger = logging.getLogger(__name__)
cover_command_topic = "cover/tydom/{id}/set_positionCmd"
cover_config_topic = "homeassistant/cover/tydom/{id}/config"
cover_position_topic = "cover/tydom/{id}/current_position"
cover_tilt_topic = "cover/tydom/{id}/current_tilt"
cover_set_position_topic = "cover/tydom/{id}/set_position"
cover_set_tilt_topic = "cover/tydom/{id}/set_tilt"
cover_attributes_topic = "cover/tydom/{id}/attributes"


class Cover:
    def __init__(self, tydom_attributes, set_position=None, mqtt=None):
        self.device = None
        self.config = None
        self.config_topic = None
        self.attributes = tydom_attributes
        self.device_id = self.attributes["device_id"]
        self.endpoint_id = self.attributes["endpoint_id"]
        self.id = self.attributes["id"]
        self.name = self.attributes["cover_name"]
        self.set_position = set_position

        if "position" in tydom_attributes:
            self.current_position = self.attributes["position"]

        if "tilt" in tydom_attributes:
            self.current_tilt = self.attributes["tilt"]

        self.mqtt = mqtt

    async def setup(self):
        self.device = {
            "manufacturer": "Delta Dore",
            "model": "Volet",
            "name": self.name,
            "identifiers": self.id,
        }
        self.config_topic = cover_config_topic.format(id=self.id)
        self.config = {
            "name": None,  # set an MQTT entity's name to None to mark it as the main feature of a device
            "unique_id": self.id,
            "command_topic": cover_command_topic.format(id=self.id),
            "set_position_topic": cover_set_position_topic.format(id=self.id),
            "position_topic": cover_position_topic.format(id=self.id),
            "payload_open": "UP",
            "payload_close": "DOWN",
            "payload_stop": "STOP",
            "retain": "false",
            "device": self.device,
            "device_class": "shutter",
        }

        if "tilt" in self.attributes:
            self.config["tilt_command_topic"] = cover_set_tilt_topic.format(id=self.id)
            self.config["tilt_status_topic"] = cover_tilt_topic.format(id=self.id)

        self.config["json_attributes_topic"] = cover_attributes_topic.format(id=self.id)

        if self.mqtt is not None:
            self.mqtt.mqtt_client.publish(
                self.config_topic, json.dumps(self.config), qos=0, retain=True
            )

    async def update(self):
        await self.setup()

        try:
            await self.update_sensors()
        except Exception as e:
            logger.error("Cover sensors Error :")
            logger.error(e)

        if self.mqtt is not None and "position" in self.attributes:
            self.mqtt.mqtt_client.publish(
                self.config["position_topic"], self.current_position, qos=0, retain=True
            )

        if self.mqtt is not None and "tilt" in self.attributes:
            self.mqtt.mqtt_client.publish(
                self.config["tilt_status_topic"], self.current_tilt, qos=0, retain=True
            )

        if self.mqtt is not None:
            self.mqtt.mqtt_client.publish(
                self.config["json_attributes_topic"],
                self.attributes,
                qos=0,
                retain=True,
            )

        logger.info("Cover created / updated : %s %s", self.name, self.id)

    async def update_sensors(self):
        for i, j in self.attributes.items():
            if (
                not i == "device_type"
                and not i == "id"
                and not i == "device_id"
                and not i == "endpoint_id"
            ):
                new_sensor = Sensor(
                    elem_name=i,
                    tydom_attributes_payload=self.attributes,
                    mqtt=self.mqtt,
                )
                await new_sensor.update()

    async def put_position(tydom_client, device_id, cover_id, position):
        logger.info("%s %s %s", cover_id, "position", position)
        if not (position == ""):
            await tydom_client.put_devices_data(
                device_id, cover_id, "position", position
            )

    async def put_tilt(tydom_client, device_id, cover_id, tilt):
        logger.info("%s %s %s", cover_id, "tilt", tilt)
        if not (tilt == ""):
            await tydom_client.put_devices_data(device_id, cover_id, "slope", tilt)

    async def put_positionCmd(tydom_client, device_id, cover_id, positionCmd):
        logger.info("%s %s %s", cover_id, "positionCmd", positionCmd)
        if not (positionCmd == ""):
            await tydom_client.put_devices_data(
                device_id, cover_id, "positionCmd", positionCmd
            )
