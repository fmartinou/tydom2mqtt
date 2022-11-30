# Changelog

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