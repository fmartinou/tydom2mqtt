#/bin/sh
docker run \
  --restart=always \
  --net=host \
  --name=tydom2mqtt \
  -e TYDOM_MAC='001A25xxxxxx' \
  -e TYDOM_IP='192.168.1.xx' \
  -e TYDOM_PASSWORD='TYDOM_PASSWORD' \
  -e MQTT_USER='MQTT_USER' \
  -e MQTT_PASSWORD='MQTT_PASSWORD*' \
  mrwiwi/tydom2mqtt

# ####### CREDENTIALS TYDOM
# TYDOM_MAC = os.environ['TYDOM_MAC'] #MAC Address of Tydom Box
# TYDOM_IP = os.environ['TYDOM_IP'] # Local ip address or mediation.tydom.com for remote connexion
# TYDOM_PASSWORD = os.environ['TYDOM_PASSWORD'] #Tydom password

# ####### CREDENTIALS MQTT
# MQTT_HOST = os.environ['MQTT_HOST']
# MQTT_USER = os.environ['MQTT_USER']
# MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
