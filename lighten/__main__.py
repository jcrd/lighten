import argparse
import sys

from gi.repository import Gio, GLib


def get_proxy(iface):
    return Gio.DBusProxy.new_sync(
        Gio.bus_get_sync(Gio.BusType.SESSION, None),
        Gio.DBusProxyFlags.NONE,
        None,
        "com.github.jcrd.lighten",
        "/com/github/jcrd/lighten",
        f"com.github.jcrd.lighten.{iface}",
        None,
    )


def set_brightness(v):
    p = get_proxy("Backlight")
    v = GLib.Variant("(u)", (v,))
    r = p.call_sync("SetBrightness", v, Gio.DBusCallFlags.NO_AUTO_START, 3000, None)
    return r.unpack()[0]


def add_brightness(v):
    p = get_proxy("Backlight")
    v = GLib.Variant("(i)", (v,))
    r = p.call_sync("AddBrightness", v, Gio.DBusCallFlags.NO_AUTO_START, 3000, None)
    return r.unpack()[0]


def restore_brightness():
    p = get_proxy("Backlight")
    r = p.call_sync(
        "RestoreBrightness", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None
    )
    return r.unpack()[0]


def normalize_brightness():
    p = get_proxy("Backlight")
    r = p.call_sync(
        "NormalizeBrightness", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None
    )
    return r.unpack()[0]


def toggle():
    p = get_proxy("Backlight")
    r = p.call_sync("ToggleAuto", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None)
    return r.unpack()[0]


def get_brightness():
    p = get_proxy("Backlight")
    r = p.call_sync("GetBrightness", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None)
    return r.unpack()[0]


def get_data():
    p = get_proxy("Sensor")
    r = p.call_sync("GetData", None, Gio.DBusCallFlags.NO_AUTO_START, 3000, None)
    return r.unpack()[0]


def main():
    parser = argparse.ArgumentParser(
        description="Control monitor brightness", prog="lighten"
    )
    sub = parser.add_subparsers(title="commands", dest="command")
    sub.required = True
    parsers = {}

    parsers["set"] = sub.add_parser("set", help="Set monitor brightness")
    parsers["set"].add_argument(
        "modifier",
        choices=["+", "-", "="],
        help="Set brightness relatively or absolutely",
    )
    parsers["set"].add_argument("value", type=int, help="Brightness value")
    parsers["get"] = sub.add_parser("get", help="Get monitor brightness")
    parsers["sensor"] = sub.add_parser("sensor", help="Get sensor data")
    parsers["status"] = sub.add_parser(
        "status", help="Get sensor data and monitor brightness"
    )
    parsers["restore"] = sub.add_parser(
        "restore", help="Restore saved monitor brightness"
    )
    parsers["normalize"] = sub.add_parser(
        "normalize", help="Set monitor brightness to sensor data value"
    )
    parsers["toggle"] = sub.add_parser(
        "toggle", help="Toggle auto adjustment of monitor brightness"
    )

    args = parser.parse_args()

    r = False
    if args.command == "set":
        if args.modifier == "+":
            r = add_brightness(args.value)
        elif args.modifier == "-":
            r = add_brightness(-args.value)
        elif args.modifier == "=":
            r = set_brightness(args.value)
    elif args.command == "sensor":
        d = get_data()
        if d != -1:
            print(d)
            return
    elif args.command == "get":
        b = get_brightness()
        if b != -1:
            print(b)
            return
    elif args.command == "status":
        d = get_data()
        b = get_brightness()
        if d != -1 and b != -1:
            print(d, b)
            return
    elif args.command == "restore":
        r = restore_brightness()
    elif args.command == "normalize":
        r = normalize_brightness()
    elif args.command == "toggle":
        r = toggle()
    if not r:
        sys.exit(1)


if __name__ == "__main__":
    main()
