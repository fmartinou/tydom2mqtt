# Changelog

# 3.5.3
- :fire: Fix Light command

# 3.5.2
- :fire: Fix HVAC actions on cooling mode

# 3.5.1
- :fire: Fix configuration not overrided when using HASS.io

# 3.5.0
- :star: Add HVAC switch mode

# 3.4.3
- :star: Add device polling 
- :star: Add HVAC cool mode
- :star: Automatically set HVAC action when setpoint > current temp

# 3.4.2
- :star: Add `PANIC` and `ACK` alarm commands
- :star: Add `state_class` to Home-Assistant energy sensors
- :fire: Fix `websocket is not defined` error
- :fire: Fix `syntax error` on light component

# 3.4.1
- :fire: Fix thermostat custom presets when not used

# 3.4.0
- :star: Add thermostat custom presets
- :fire: Fix uncaught exception at startup

# 3.3.1
- :fire: Fix HA 2023.8 mqtt entity naming convention warnings
- :fire: Fix Alarm attributes not updated

# 3.3.0
- :star: Add support for Radiator valves with thermostat
- :star: Home-Assistant sensors improvements (naming, ON/OFF value support...)
- :fire: Reconnect when connection to the Tydom is lost
- :fire: Fix update_sensors function bad filtering

# 3.2.0
- :star: Add `awning` devices
- :star: Add `other` devices

# 3.1.2
- :fire: Fix command parsing

# 3.1.1
- :fire: Fix startup error

# 3.1.0
- :star: Retrieve tydom credentials from Delta Dore cloud
- :fire: Enable SSL unsafe legacy renegotiation using ssl options instead of adding an openssl_conf.cnf file

# 3.0.2
- :star: Add `retain: true` to mqtt published message to avoid losing states when mqtt broker restarts

# 3.0.1
- :fire: Fix `'module' object is not callable` on several sensors

### 3.0.0
- :star: Add support for Smoke detectors (Tyxal DFR)
- :star: Add graceful shutdown
- :star: Add configuration validation
- :star: Cleanup code (wip)
- :fire: Make alarm pin code optional
- :fire: Mask sensitive configuration values in logs
- :fire: Fix log levels

### 2.6.6
- :fire: Fix regression because of Linux Alpine upgrade (`3.17` -> `3.16`)

### 2.6.5
- :fire: Revert the deletion of the AUTO boiler mode (`2.6.3`)

### 2.6.4
- :fire: Fix sensors for Kline sliding openings

### 2.6.3
- :fire: Replace hold_mode by preset_mode because of HA 2022.9 deprecation

### 2.6.2
- :fire: Fix unknown HA device classes

### 2.6.1
- :fire: Poll one device at a time to avoid sporadic Tybox DOS

### 2.6.0
- :star: Add support for TYPASS and Tywatt 5100 gaz sensor

### 2.5.0
- :star: Add sensor unknown for motion & door detectors
- :fire: Delete duplicate binary sensors
- :fire: Force value sensor to OFF/ON

### 2.4.0
- :star: Add support for Tywatt energy distribution (clamp)

### 2.3.1
- :fire: Fix cover config publication

### 2.3.0
- :star: Add cover tilt support
- :fire: Fix binary sensors created but not updated on HA

### 2.2.0
- :star: Add `Tywatt` support

### 2.1.0
- :star: Set Tydom IP and MAC as required
- :star: The Tydom Alarm PIN as optional.
- :star: Code massive rework (logger, statics, formatting...)
- :fire: Handle missing WWW-Authenticate header
- :fire: Fix alarm module
- :fire: Fix some logger bad calls

### 2.0.1
- :fire: Fix sensor type for windows giving status (OPEN, CLOSE, OPEN_HOPPER)
- :fire: Fix wrong binary_sensor type in some cases

### 2.0.0
- :star: Add boiler `AUTO` mode
- :star: Reduce Docker image size (`alpine` based)
- :star: Allow ability to run the image without `tty`