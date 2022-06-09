import argparse

import dbus


def main():
    parser = argparse.ArgumentParser(
        description="Control monitor brightness", prog="lighten"
    )
    parser.add_argument(
        "command",
        choices=["set", "inc", "up", "dec", "down", "restore"],
        help="Brightness control command",
    )
    parser.add_argument(
        "value", nargs="?", type=int, default=0, help="Brightness value"
    )

    args = parser.parse_args()

    service = dbus.SessionBus().get_object(
        "com.github.jcrd.lighten", "/com/github/jcrd/lighten"
    )

    def sub_brightness(value):
        service.add_brightness(-value)

    cmds = {
        "set": service.set_brightness,
        "inc": service.add_brightness,
        "up": service.add_brightness,
        "dec": sub_brightness,
        "down": sub_brightness,
    }

    if args.command == "restore":
        service.restore_brightness()
    else:
        cmds[args.command](args.value)


if __name__ == "__main__":
    main()
