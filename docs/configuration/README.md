# Configuration
`tydom2mqtt` can be configured using environment variables.

## Environment variables

Please note that only one of DELTADORE_LOGIN + DELTADORE_PASSWORD or TYDOM_PASSWORD is needed as your Delta Dore account is used to retrieve the Tydom password

| Environment variable   | Required       | Supported values                                  | Default value when missing |
|------------------------|----------------|---------------------------------------------------|----------------------------|
| TYDOM_MAC              | :red_circle:   | Tydom MAC address (starting with `001A...`)       |                            |
| DELTADORE_LOGIN        | :red_circle:   | Delta Dore account login                          |                            |
| DELTADORE_PASSWORD     | :red_circle:   | Delta Dore account password                       |                            |
| TYDOM_PASSWORD         | :red_circle:   | Tydom password                                    |                            |
| TYDOM_IP               | :white_circle: | Tydom IPv4 address or FQDN                        | `mediation.tydom.com`      |
| TYDOM_ALARM_PIN        | :white_circle: | Tydom Alarm PIN                                   | `None`                     |
| TYDOM_ALARM_HOME_ZONE  | :white_circle: | Tydom alarm home zone                             | `1`                        |
| TYDOM_ALARM_NIGHT_ZONE | :white_circle: | Tydom alarm night zone                            | `2`                        |
| MQTT_HOST              | :white_circle: | Mqtt broker IPv4 or FQDN                          | `localhost`                |
| MQTT_PORT              | :white_circle: | Mqtt broker port                                  | `1883`                     |
| MQTT_USER              | :white_circle: | Mqtt broker user if authentication is enabled     | `None`                     |
| MQTT_PASSWORD          | :white_circle: | Mqtt broker password if authentication is enabled | `None`                     |
| MQTT_SSL               | :white_circle: | Mqtt broker ssl enabled                           | `false`                    |
| LOG_LEVEL              | :white_circle: | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)   | `ERROR`                    |
| THERMOSTAT_CUSTOM_PRESETS | :white_circle: | Set custom Presets for THERMOSTAT like [4890](https://www.deltadore.fr/domotique/gestion-chauffage/micromodule-recepteur/recepteur-rf4890-ref-6050615) <br/> format : { 'preset': 'temp'} (exemple { 'ECO' : '17' })   |                     |

## Complete example

<!-- tabs:start -->
#### **Docker Compose**
```yaml
version: '3'

services:
  tydom2mqtt:
    image: fmartinou/tydom2mqtt
    container_name: tydom2mqtt
    environment:
      - TYDOM_MAC=001A25XXXXXX
      - TYDOM_PASSWORD=azerty123456789
      - TYDOM_IP=192.168.1.33
```
#### **Docker**
```bash
docker run -d --name tydom2mqtt \
  -e TYDOM_MAC="001A25XXXXXX" \
  -e TYDOM_PASSWORD="azerty123456789" \
  -e TYDOM_IP="192.168.1.33" \  
  fmartinou/tydom2mqtt
```
<!-- tabs:end -->

## THERMOSTAT_CUSTOM_PRESETS parameter

### Why this parameter ?

For systems like underfloor heating system, delta dore sells to other mark like Thermor some equipment like  [4890](https://www.deltadore.fr/domotique/gestion-chauffage/micromodule-recepteur/recepteur-rf4890-ref-6050615). 
The problem is these sondes are controlled by an offline Thermostat. But each 4890 are independant and use X3D to set temperature, the offline thermostat just connect to it and ask them to change the target temperature, the sondes itself is an independant thermostat with current temperature (depends on system, internal temperature or offline thermostat temperature). The 4890 is compatible with Tydom and can be control by offline thermostat and Tydom.
But each of 4890 are not a full themostat and doesn't have presets, each controller must set their own presets if needed.

### How to use

Set environment variables : THERMOSTAT_CUSTOM_PRESETS with a map of compatible presets ("STOP", "ANTI_FROST", "ECO", "COMFORT", "AUTO")

exemple :

```bash
docker run -d --name tydom2mqtt \
  -e TYDOM_MAC="001A25XXXXXX" \
  -e TYDOM_PASSWORD="azerty123456789" \
  -e TYDOM_IP="192.168.1.33" \ 
  -e THERMOSTAT_CUSTOM_PRESETS='{"ECO": "17", "COMFORT": "20"}'
  fmartinou/tydom2mqtt
```
