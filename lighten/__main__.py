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


def call(method, arg=None, iface="Backlight", multi=False):
    try:
        p = get_proxy(iface)
        r = p.call_sync(
            method, arg, Gio.DBusCallFlags.NO_AUTO_START, 3000, None)
        if multi:
            return r.unpack()
        else:
            return r.unpack()[0]
    except GLib.GError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def set_brightness(v):
    return call("SetBrightness", GLib.Variant("(u)", (v,)))


def add_brightness(v):
    return call("AddBrightness", GLib.Variant("(i)", (v,)))


def restore_brightness():
    return call("RestoreBrightness")


def normalize_brightness():
    return call("NormalizeBrightness")


def set_auto(v):
    return call("SetAuto", GLib.Variant("(s)", (v,)))


def get_brightness():
    vs = call("GetBrightness", multi=True)
    return vs[0], vs[1]


def get_data():
    return call("GetData", iface="Sensor")


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
    parsers["auto"] = sub.add_parser(
        "auto", help="Set auto adjustment of monitor brightness"
    )
    parsers["auto"].add_argument(
        "state",
        choices=["toggle", "on", "off"],
        help="Turn auto adjustment on, off, or toggle",
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
        b, _ = get_brightness()
        if b != -1:
            print(b)
            return
    elif args.command == "status":
        d = get_data()
        b, base = get_brightness()
        if d != -1 and b != -1:
            print("sensor:", d)
            print("monitor:", b)
            print("baseline:", base)
            return
    elif args.command == "restore":
        r = restore_brightness()
    elif args.command == "normalize":
        r = normalize_brightness()
    elif args.command == "auto":
        r = set_auto(args.state)
    if not r:
        sys.exit(1)


if __name__ == "__main__":
    main()
