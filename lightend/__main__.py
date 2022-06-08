import subprocess

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

BUS_NAME = "com.github.jcrd.lighten"


class Service(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName(BUS_NAME, dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/com/github/jcrd/lighten")

        self.loop = GLib.MainLoop()

    def run(self):
        self.loop.run()

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="u", out_signature="b")
    def set_brightness(self, value):
        return ddcutil(value, absolute=True)

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="i", out_signature="b")
    def add_brightness(self, value):
        return ddcutil(value)


def ddcutil(value, absolute=False):
    cmd = ["ddcutil", "setvcp", "10"]
    if not absolute:
        sign = "+"
        if value < 0:
            sign = "-"
        cmd.append(sign)
    cmd.append(str(abs(value)))

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    Service().run()


if __name__ == "__main__":
    main()
