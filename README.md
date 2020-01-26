# tydom2mqtt
Link a tydom hub to a mqtt server
Based on https://github.com/cth35/tydom_python


Needed packages : pip3 install websockets requests tendo

Add your credentials to main.py, then python3 main.py to test, if all is good, do a

sh tydom2mqtt_restarter.sh

The tydom2mqtt_restarter.sh script is made to restart in case of fatal error.
Disconnections from both servers are handled with automatic reconnections.


Alarm is readonly for now, (i've soldered a remote to optocouplers and an ESP8266 with esphome to set it from home assisant, a least it's very reliable !).
