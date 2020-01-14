# tydom2mqtt
Link a tydom hub to a mqtt server
Based on https://github.com/cth35/tydom_python

Preq : pip3 install websockets requests

Add your credentials to main.py, then python3 main.py to test

The tydom2mqtt_restarter.sh script is made to restart in case of fatal error, do a sh tydom2mqtt_restarter.sh.

Disconnections from both servers are handled with automatic reconnections.
