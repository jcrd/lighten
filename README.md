# lighten

Lighten is an intelligent monitor brightness control utility.

## Usage

Enable the daemon with: `systemctl --user enable --now lightend`

Then control your monitor's brightness with `lighten`:

```txt
usage: lighten [-h] {set,inc,up,dec,down} value

Control monitor brightness

positional arguments:
  {set,inc,up,dec,down}
                        Brightness control command
  value                 Brightness value

options:
  -h, --help            show this help message and exit
```

## License

This project is licensed under the MIT License (see [LICENSE](LICENSE)).
