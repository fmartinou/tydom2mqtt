# tydom2MQTT

![Docker pulls](https://img.shields.io/docker/pulls/fmartinou/tydom2mqtt)
![License](https://img.shields.io/github/license/fmartinou/tydom2mqtt)
![Travis](https://img.shields.io/travis/fmartinou/tydom2mqtt/master)

> **Link a [Delta Dore Tydom hub](https://www.deltadore.fr/app-tydom) to an mqtt broker.**

> [Home Assistant tydom2mqtt official thread](https://community.home-assistant.io/t/tydom2mqtt-delta-dore-custom-component-wip/151333)

*Forked from [mrwiwi/tydom2mqtt](https://github.com/mrwiwi/tydom2mqtt) with the following improvements:*
- Multi-arch lighter Docker images
- [Travis](https://app.travis-ci.com/github/fmartinou/tydom2mqtt) continuous integration
- [Python PEP8 code style](https://www.python.org/dev/peps/pep-0008/) enforcement
- Boiler `AUTO` mode
- Better default values
- Improved documentation

## Why?
Deltadore doesn't provide any public API so this project is a humble try to fix that injustice. \
Hardware is so good, that's really a shame !

## Features
> Push event based (websocket) to instantly get changes (inspired by [tydom_python](https://github.com/cth35/tydom_python))

> Out-of-the-box [Home-Assistant](https://www.home-assistant.io/) integration thanks to [Mqtt discovery](https://www.home-assistant.io/docs/mqtt/discovery/) 

> Automatic reconnection to Tydom on connection drop

> Automatic reconnection to the Mqtt broker on connection drop

## Getting started

### Prerequisites
- MQTT broker (Mosquitto, MQTT Home-Assistant addon...)
- Docker engine (for Docker users)
- Hass-io (for Hass.io users)

### Configuration
tydom2mqtt can be configured by using the following environment variables.

| Environment variable   | Required       | Supported values                                  | Default value when missing |
|------------------------|----------------|---------------------------------------------------|----------------------------|
| TYDOM_MAC              | :red_circle:   | Tydom MAC address (starting with `001A...`)       |                            |
| TYDOM_PASSWORD         | :red_circle:   | Tydom password                                    |                            |
| TYDOM_IP               | :white_circle: | Tydom IPv4 address or FQDN                        | mediation.tydom.com        |
| TYDOM_ALARM_PIN        | :white_circle: | Tydom Alarm PIN                                   | None                       |
| TYDOM_ALARM_HOME_ZONE  | :white_circle: | Tydom alarm home zone                             | 1                          |
| TYDOM_ALARM_NIGHT_ZONE | :white_circle: | Tydom alarm night zone                            | 2                          |
| MQTT_HOST              | :white_circle: | Mqtt broker IPv4 or FQDN                          | localhost                  |
| MQTT_PORT              | :white_circle: | Mqtt broker port                                  | 1883                       |
| MQTT_USER              | :white_circle: | Mqtt broker user if authentication is enabled     | None                       |
| MQTT_PASSWORD          | :white_circle: | Mqtt broker password if authentication is enabled | None                       |
| MQTT_SSL               | :white_circle: | Mqtt broker ssl enabled                           | false                      |

### Hass.io users
Use this [addon repository](https://github.com/WiwiWillou/hassio_addons.git). \
That's all! (thanks to Mqtt auto discovery, no further configuration needed)

### Docker users
Run [`fmartinou/tydom2mqtt`](https://hub.docker.com/repository/docker/fmartinou/tydom2mqtt) with the appropriate environment variables.

*N.B. The Docker image is working on the `arm/v6`, `arm/v7`, `arm64/v8`, `amd64` platforms.*

```yaml
# Docker-Compose example
version: '3'

services:
  tydom2mqtt:
    image: fmartinou/tydom2mqtt
    container_name: tydom2mqtt
    environment:
      - TYDOM_MAC=001A2502ACE8
      - TYDOM_PASSWORD=azerty123456789
      - TYDOM_IP=192.168.1.33
```

## FAQ

### How to reset my tydom password?
In october 2021, Deltadore has released a new version of its Tydom app (v4+) preventing to set or reset the Tydom password.

To set/reset your password, better download the previous version (v3+) which still allows to do it ([Aptoide link](https://tydom.fr.aptoide.com/app?store_name=aptoide-web&app_id=58618221)).

### How to prevent my tydom to communicate with deltadore servers?
If you're concerned about your privacy, you can perform the following actions:
1. Configure you router to forbid your Tydom hub to access internet
2. Find your tydom local IP address and use it as `TYDOM_IP` value

### Why alarm motion sensor activity isn't reported?
- Alarm motion sensor activity isn't reported but when the alarm is fired then you get a cdata message so you can get the info (only when alarm is armed, pending and triggered).

## TODO
- Fix parsing of cdata msg type (will not crash anymore in the meantime), coming from an action from an alarm remote (and probably other things), we can get which remote had an action on alarm with it.
- Fork it to a proper Home Assistant integration with clean on-boarding
- Add climate, garagedoor, etc.
- Build a web frontend to see and test (use [frontail](https://github.com/mthenw/frontail) for now)

## Contact & Support

- Create a [GitHub issue](https://github.com/fmartinou/tydom2mqtt/issues) for bug reports, feature requests, or questions
- Add a ⭐️ [star on GitHub](https://github.com/fmartinou/tydom2mqtt) to support the project!

## Developer guide
[Please find here the developer guide](DEV.md)

## Changelog
[Please find here the changelog](CHANGELOG.md)

## License

This project is licensed under the [MIT license](https://github.com/fmartinou/teleinfo-mqtt/blob/master/LICENSE).