# lighten

[![unittest](https://github.com/jcrd/lighten/actions/workflows/unittest.yml/badge.svg)](https://github.com/jcrd/lighten/actions/workflows/unittest.yml)

lighten is an intelligent monitor brightness control utility that regulates
brightness based on ambient light.

It requires a HID-based light sensor that regularly reports ambient light values.
See [arduino-lighten][arduino-lighten] for an Arduino-based option.

[arduino-lighten]: https://github.com/jcrd/arduino-lighten

## Features

- saves ambient light to monitor brightness correlations
- restores monitor brightness...
  - when ambient light changes significantly
  - on demand
  - at startup
  - upon wakeup from sleep
  - at regular intervals as time passes
- provides a DBus service and CLI client

## Usage

Enable the daemon with: `systemctl --user enable --now lightend`

Then control your monitor's brightness with `lighten`:

```txt
usage: lighten [-h] {set,get,sensor,status,restore,normalize} ...

Control monitor brightness

options:
  -h, --help            show this help message and exit

commands:
  {set,get,sensor,status,restore,normalize}
    set                 Set monitor brightness
    get                 Get monitor brightness
    sensor              Get sensor data
    status              Get sensor data and monitor brightness
    restore             Restore saved monitor brightness
    normalize           Set monitor brightness to sensor data value
```

## Configuration

lighten looks for a configuration file at
`$XDG_CONFIG_HOME/lighten/lightend.conf` or falls back to
`$HOME/.config/lighten/lightend.conf` if `$XDG_CONFIG_HOME` is unset.

See [lightend.conf](lightend.conf) for the format and defaults.

The `[sensor]` section is required and must contain the `vendor_id` and
`product_id` keys which specify the vendor ID and product ID of the HID device
to use, respectively.

These can be obtained using `lsusb`:

```
Bus 005 Device 002: ID 239a:8111 Adafruit QT Py ESP32-S2
```

The sixth column contains the IDs in the format: `vendor:product`.

The `[params]` section may contain the following keys:

- `save_fidelity`: range of values to be subsumed when saving a new ambient
light value
- `max_deviation`: maximum difference between current and saved ambient light
value for restoration
- `change_threshold`: difference between ambient light values that warrants
restoring saved brightness
- `restore_interval`: seconds after which the ambient light will be checked to
restore saved brightness
- `restore_range`: number of `restore_interval` cycles after which brightness
will be compared to the value recorded at the start of this range

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)).
