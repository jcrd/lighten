import argparse
import sys

from gi.repository import Gio, GLib


def main():
    parser = argparse.ArgumentParser(
        description="Control monitor brightness", prog="lighten"
    )
    parser.add_argument(
        "command",
        choices=["set", "inc", "up", "dec", "down", "restore", "get"],
        help="Brightness control command",
    )
    parser.add_argument(
        "value", nargs="?", type=int, default=0, help="Brightness value"
    )

    args = parser.parse_args()

    proxy = Gio.DBusProxy.new_sync(
        Gio.bus_get_sync(Gio.BusType.SESSION, None),
        Gio.DBusProxyFlags.NONE,
        None,
        "com.github.jcrd.lighten",
        "/com/github/jcrd/lighten",
        "com.github.jcrd.lighten.Backlight",
        None,
    )

    def set_brightness(v):
        v = GLib.Variant("(u)", (v,))
        r = proxy.call_sync(
            "SetBrightness", v, Gio.DBusCallFlags.NO_AUTO_START, 3000, None
        )
        return r.unpack()[0]

    def add_brightness(v):
        v = GLib.Variant("(i)", (v,))
        r = proxy.call_sync(
            "AddBrightness", v, Gio.DBusCallFlags.NO_AUTO_START, 3000, None
        )
        return r.unpack()[0]

    def sub_brightness(v):
        return add_brightness(-v)

    def restore_brightness():
        r = proxy.call_sync(
            "RestoreBrightness", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None
        )
        return r.unpack()[0]

    def get_brightness():
        r = proxy.call_sync(
            "GetBrightness", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None
        )
        return r.unpack()[0]

    cmds = {
        "set": set_brightness,
        "inc": add_brightness,
        "up": add_brightness,
        "dec": sub_brightness,
        "down": sub_brightness,
    }

    if args.command == "get":
        b = get_brightness()
        if b != -1:
            print(b)
            return
        r = False
    elif args.command == "restore":
        r = restore_brightness()
    else:
        r = cmds[args.command](args.value)
    if not r:
        sys.exit(1)


if __name__ == "__main__":
    main()
