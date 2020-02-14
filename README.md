# tydom2mqtt
Link a Delta Dore's tydom hub to a mqtt broker, working flawlessly here for days with the help of systemd's restarting mechanism.
The script works in background, with remote mode by default (see todo), by rollback in local mode if necessary (offline mode).

Based on https://github.com/cth35/tydom_python

Recommanded setup : any Linux server with systemd management and python3.8.
Home assistant's MQTT auto discovery enabled. For other systemd you just add devices like any MQTT devices.

Needed packages : "pip3 install websockets requests gmqtt"

- Add your credentials to main.py
- Put all the *.py files in a folder of your choice (Hassio users : by default i've put them in the share folder of hassio for backup purposes "/usr/share/hassio/share/tydom/")
- Put the tydom.service file in the folder of your choice (/usr/lib/systemd/system/ if you don't know where)
- Change the path if the main.py file in tydom.service
- with commandline, do "systemctl enable tydom.service"
- with commandline, do "systemctl start tydom.service"
- with commandline, check "systemctl status tydom.service" or with journalctl.

Disconnections from both servers are handled with automatic reconnections.

If you don't use hassio / home assistant, check on the cover and alarm py files to see or modify the topics !

Alarm is readonly for now, (i've soldered a remote to optocouplers and an ESP8266 with esphome to set it from home assisant, a least it's very reliable !).

i don't have climate or lights to test, feel free to help !

TODO (but i've got no more time...) :

- Fix that annoying code 1006 systematic deconnection after 60s when using local mode (new since december, not before).
- HACS / Docker versions
- Fork it to a proper Home Assistant integration with clean onboarding
- Add climate, lights, etc.
- Build a web frontend to see and test (use frontail for now)
- Add a folder of images to document where to solder on alarm remote and ESPHome configuration.
