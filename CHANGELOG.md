## Changelog

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