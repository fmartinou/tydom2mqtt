# tydom2mqtt

https://community.home-assistant.io/t/tydom2mqtt-delta-dore-custom-component-wip/151333

Link a Delta Dore's Tydom hub to a mqtt broker, working flawlessly here for days with the help of systemd's restarting mechanism.
The script works in background, with remote mode by default (see todo), and rollback in local mode if necessary (offline mode).
Disconnections from both servers are handled with automatic reconnections.

Not based on a poll mechanism but on push from websocket, i.e. it constantly pings the tydom hub to keep alive the connection and receive updates instantly.

Home assistant users : Use MQTT auto discovery, no further config necessary ! (Hassio docker install + MQTT addon on top of Ubuntu server is my personal setup.)
For other home automation systems you just add devices like any MQTT devices, check on the cover and alarm py files to see or modify the topics !

Based initialy on https://github.com/cth35/tydom_python

Recommanded setup : any Linux OS with systemd management and python3.7

Needed packages : "pip3 install websockets requests gmqtt"
Opional packages : "pip3 install sdnotify" // If you want the systemd management (start, autorestart...)


- Clone / Put all the *.py files in a folder of your choice (Hassio users : by default i've put them in the share folder of hassio for backup purposes "/usr/share/hassio/share/tydom/") // Not the local / www folder !
- Add your credentials to main.py
- TEST IT ! 'python3 main.py'

If it works and you want the recommanded systemd mechanism :

- Put the tydom.service file in the folder of your choice (/usr/lib/systemd/system/ if you don't know where)
- Change the path of the main.py file in tydom.service
- with commandline, do "systemctl enable /pathto/tydom.service" // It will start on boot, it's a set and forget !
- with commandline, do "systemctl start tydom.service"
- with commandline, check "systemctl status tydom.service" or with journalctl.

- To force a restart from your system, publish anything to hassio/tydom/kill, i will exit the script, systemd will restart it clean.

Alarm is readonly for now, (i've soldered a remote to optocouplers and an ESP8266 with esphome to set it from home assisant, a least it's very reliable !).

i don't have climate or lights to test, feel free to help !

TODO (but i've got no more time...) :

- x DONE ! (websockets error with ping timeout) Fix that annoying code 1006 systematic deconnection after 60s when using local mode (new since december, not before).
- Fix parsing of cdata msg type (will not crash anymore in the meantime), coming from an action from a alarm remote (and probably other things), we can get which remote had an action on alarm with it.
- Add all the attributes as json for home assistant (can see defect, etc. on attributes)
- X DONE ! Isolate parser in a class maybe...
- HACS / Docker versions
- Fork it to a proper Home Assistant integration with clean onboarding
- Add climate, lights, etc.
- Build a web frontend to see and test (use frontail for now)
- Add a folder of images to document where to solder on alarm remote and ESPHome configuration. // Add alarm handling, see mgcrea node tydom-client (what a guy :))


Home Assistant User :

To fix the not updating / ask update on restart (because the config part as already happenned when hassio boot), create that script on hass, and create an automation to execute it when hass start !

```
update_tydom2mqtt:
  alias: Tydom Update
  sequence:
  - data:
      payload: '{ "update" }'
      topic: hassio/tydom/update
    service: mqtt.publish
```
 
