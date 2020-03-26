import json
import time
from datetime import datetime

cover_command_topic = "cover/tydom/{id}/set_positionCmd"
cover_config_topic = "homeassistant/cover/tydom/{id}/config"
cover_position_topic = "cover/tydom/{id}/current_position"
cover_set_postion_topic = "cover/tydom/{id}/set_position"
cover_attributes_topic = "cover/tydom/{id}/attributes"


class Cover:
    def __init__(self, tydom_attributes, set_position=None, mqtt=None):
        
        self.attributes = tydom_attributes

        self.id = self.attributes['id']
        self.name = self.attributes['cover_name']
        self.current_position = self.attributes['position']
        self.set_position = set_position
        self.mqtt = mqtt

    # def id(self):
    #     return self.id

    # def name(self):
    #     return self.name

    # def current_position(self):
    #     return self.current_position

    # def set_position(self):
    #     return self.set_position

    # def attributes(self):
    #     return self.attributes

    async def setup(self):
        self.device = {}
        self.device['manufacturer'] = 'Delta Dore'
        self.device['model'] = 'Volet'
        self.device['name'] = self.name
        self.device['identifiers'] = self.id

        self.config_topic = cover_config_topic.format(id=self.id)
        self.config = {}
        self.config['name'] = self.name
        self.config['unique_id'] = self.id
        # self.config['attributes'] = self.attributes
        self.config['command_topic'] = cover_command_topic.format(id=self.id)
        self.config['set_position_topic'] = cover_set_postion_topic.format(id=self.id)
        self.config['position_topic'] = cover_position_topic.format(id=self.id)
        self.config['json_attributes_topic'] = cover_attributes_topic.format(id=self.id)

        self.config['payload_open'] = "UP"
        self.config['payload_close'] = "DOWN"
        self.config['payload_stop'] = "STOP"
        self.config['retain'] = 'false'
        self.config['device'] = self.device
        # print(self.config)

        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.config_topic, json.dumps(self.config), qos=0)
        # setup_pub = '(self.config_topic, json.dumps(self.config), qos=0)'
        # return(setup_pub)

    async def update(self):
        await self.setup()
        self.position_topic = cover_position_topic.format(id=self.id, current_position=self.current_position)
        
        if (self.mqtt != None):
            self.mqtt.mqtt_client.publish(self.position_topic, self.current_position, qos=0, retain=True)
            # self.mqtt.mqtt_client.publish('homeassistant/sensor/tydom/last_update', str(datetime.fromtimestamp(time.time())), qos=1, retain=True)
            self.mqtt.mqtt_client.publish(self.config['json_attributes_topic'], self.attributes, qos=0)

        print("Cover created / updated : ", self.name, self.id, self.current_position)

        # update_pub = '(self.position_topic, self.current_position, qos=0, retain=True)'
        # return(update_pub)
       






    async def put_position(tydom_client, cover_id, position):
        print(cover_id, 'position', position)
        if not tydom_client.connection.open:
            print('MQTT req : Websocket not opened, reconnect...')
            await tydom_client.connect()
            await tydom_client.put_devices_data(cover_id, 'position', position)

        else:
            if not (position == ''):
                await tydom_client.put_devices_data(cover_id, 'position', position)

    async def put_positionCmd(tydom_client, cover_id, positionCmd):
        print(cover_id, 'positionCmd', positionCmd)
        if not tydom_client.connection.open:
            print('MQTT req : Websocket not opened, reconnect...')
            await tydom_client.connect()
            await tydom_client.put_devices_data(cover_id, 'positionCmd', positionCmd)

        else:
            if not (positionCmd == ''):
                await tydom_client.put_devices_data(cover_id, 'positionCmd', positionCmd)
