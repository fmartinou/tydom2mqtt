# Configuration
`tydom2mqtt` can be configured using environment variables.

## Environment variables

| Environment variable   | Required       | Supported values                                  | Default value when missing |
|------------------------|----------------|---------------------------------------------------|----------------------------|
| TYDOM_MAC              | :red_circle:   | Tydom MAC address (starting with `001A...`)       |                            |
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
