# tydom2mqtt
Link a Delta Dore's tydom hub to a mqtt server
Based on https://github.com/cth35/tydom_python


Needed packages : "pip3 install websockets requests"

- Add your credentials to main.py
- Put the tydom.service file in the folder of your choice (/usr/lib/systemd/system/ if you don't know where)
- Change the path if the main.py file in tydom.service (by default i've put it in the share folder of hassio for backup purposes)
- with commandline, do "systemctl enable tydom.service"
- with commandline, do "systemctl start tydom.service"
- with commandline, check "systemctl status tydom.service" or with journalctl.

Disconnections from both servers are handled with automatic reconnections.

If you don'y use hassio / home assistant, feel free to contribute !


Alarm is readonly for now, (i've soldered a remote to optocouplers and an ESP8266 with esphome to set it from home assisant, a least it's very reliable !).

i don't have climate or lights to test, feel free to help !
