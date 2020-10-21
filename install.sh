#/bin/sh
docker run \
  --restart=always \
  --net=host \
  --name=tydom2mqtt \
  -e TYDOM_MAC='001A25xxxxxx' \
  -e TYDOM_IP='192.168.1.xx' \
  -e TYDOM_PASSWORD='TYDOM_PASSWORD' \
  -e TYDOM_ALARM_PIN = None \
  -e TYDOM_ALARM_HOME_ZONE = 1 \
  -e TYDOM_ALARM_NIGHT_ZONE = 2 \
  -e MQTT_USER='MQTT_USER' \
  -e MQTT_PASSWORD='MQTT_PASSWORD' \
  -e MQTT_PORT='MQTT_PORT' \
  -e MQTT_SSL='MQTT_SSL' \
  bbo76/tydom2mqtt_edge

# TYDOM_IP, MQTT_PORT and MQTT_SLL are optional.



# ####### CREDENTIALS TYDOM
# TYDOM_MAC = os.environ['TYDOM_MAC'] #MAC Address of Tydom Box
# TYDOM_IP = os.environ['TYDOM_IP'] # Local ip address or mediation.tydom.com for remote connexion
# TYDOM_PASSWORD = os.environ['TYDOM_PASSWORD'] #Tydom password

# ####### CREDENTIALS MQTT
# MQTT_HOST = os.environ['MQTT_HOST']
# MQTT_USER = os.environ['MQTT_USER']
# MQTT_PASSWORD = os.environ['MQTT_PASSWORD']
