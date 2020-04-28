# tydom2MQTT

https://community.home-assistant.io/t/tydom2mqtt-delta-dore-custom-component-wip/151333

Link a Delta Dore's Tydom hub to a mqtt broker. Unofficial with no public API, so this project is an humble try to fix that injustice. (hardware is so good, that's really a shame !)

Disconnections from both servers are handled with automatic reconnections.

Not based on a pull mechanism but on push from websocket, i.e. it regulary ask the tydom hub to refresh to keep alive the connection and receive updates instantly.

Based initialy on https://github.com/cth35/tydom_python

# PREREQ :

- You need a fully functional MQTT broker before using it (MQTT official addon, mosquitto on linux, etc.) and a user/pass to access it.

# HASSIO USERS (recommended choice - multiarch) :

- Addon repository : https://github.com/WiwiWillou/hassio_addons.git
- Use MQTT auto discovery, no further config necessary ! 


# DOCKER USERS (x86 only - fork it and change base image in Dockerfile if you need others arch):

You need a functional Docker before using it.

You just need the install.sh to download, mod it with your credentials (Tydom and MQTT - MQTT_HOST and TYDOM_IP are optionals, defaulting to localhost and delta dore servers respectively.), then :

```
sh install.sh
```


# NOT ON HASSIO :

- For other home automation systems, install docker version then you just add devices like any MQTT devices, check on the cover and alarm py files to see or modify the topics !


ALL :
- To force a restart from your system, publish anything to hassio/tydom/kill, it will exit the script, forever.py will restart it clean.

I don't have climate or lights to test, feel free to help !

# TODO (but i've got no more time...) :

- x DONE ! (websockets error with ping timeout) Fix that annoying code 1006 systematic deconnection after 60s when using local mode (new since december, not before).
- Fix parsing of cdata msg type (will not crash anymore in the meantime), coming from an action from a alarm remote (and probably other things), we can get which remote had an action on alarm with it.
- X DONE ! Add all the attributes as json for home assistant (can see defect, etc. on attributes)
- X DONE ! Isolate parser in a class maybe...
- X DONE ! Hassio addon version
- Fork it to a proper Home Assistant integration with clean onboarding
- Add climate, garagedoor, etc.
- Build a web frontend to see and test (use frontail for now)

# WHAT WE CAN'T DO ?

- Alarm's motion sensor activity isn't reported, but when alarm is fired there is a cdata message that could have the info, but it's only when alarm is armed and pending / triggered.

# Home Assistant / Hassio User last fix :

To fix the not updating / ask update on restart (because the config part has already happenned when hassio boot), create that script on hass, and create an automation to execute it when hass start ! - We could use birth payload be it ask for some configuration in yaml...

```
update_tydom2mqtt:
  alias: Tydom Update
  sequence:
  - data:
      payload: '{ "update" }'
      topic: hassio/tydom/update
    service: mqtt.publish
```

PR are most welcome !


# Descriptions of files

tydomConnector handle the connection with websocket, it is instaciated by the main script where initial connection and if necessary reconnections are made + passing incoming message from the tydom hub the the tydomMessageHandler, where the parsing of data is made (proabbaly lot of optimisation is possible here) and where new devices are instanciated with the corresponding classes.

MQTT is a lot easier to manage :)
