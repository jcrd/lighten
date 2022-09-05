# lighten

[![unittest](https://github.com/jcrd/lighten/actions/workflows/unittest.yml/badge.svg)](https://github.com/jcrd/lighten/actions/workflows/unittest.yml)
[![Copr build status](https://copr.fedorainfracloud.org/coprs/jcrd/lighten/package/lighten/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/jcrd/lighten/package/lighten/)

lighten is an intelligent monitor brightness control utility that regulates
brightness based on ambient light.

It requires a HID-based light sensor that regularly reports ambient light values.
See [arduino-lighten][arduino-lighten] for an Arduino-based option.

[arduino-lighten]: https://github.com/jcrd/arduino-lighten

## Packages

- Fedora ([copr][copr])

  ```sh
  dnf copr enable jcrd/lighten
  dnf install lighten
  ```

[copr]: https://copr.fedorainfracloud.org/coprs/jcrd/lighten/

## Features

- saves ambient light to monitor brightness correlations
- restores monitor brightness...
  - when ambient light changes significantly
  - on demand
  - at startup
  - upon wakeup from sleep
  - at regular intervals as time passes
- provides a DBus service and CLI client

## Initial setup

lighten uses [ddcutil][ddcutil] to control monitor brightness.
This tool requires read/write access to `/dev/i2c` video card devices. In order to use it without root permissions:

1. Add user to `i2c` group:

    ```sh
    sudo usermod <user-name> -aG i2c
    ```

2. Copy ddcutil's udev rule into place:

    ```sh
    sudo cp /usr/share/ddcutil/data/45-ddcutil-i2c.rules /etc/udev/rules.d
    ```

3. Reload and trigger the new rule:

    ```sh
    sudo udevadm control --reload
    sudo udevadm trigger
    ```

See [this document][i2cperm] for more information.

[ddcutil]: https://www.ddcutil.com/
[i2cperm]: https://www.ddcutil.com/i2c_permissions/

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

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)).
