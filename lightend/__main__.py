import logging
import os
from pathlib import Path

import dbus
import dbus.mainloop.glib
import dbus.service
from gi.repository import GLib

import lightend.ddcutil as ddcutil
from lightend.database import DB
from lightend.debouncer import Debouncer

BUS_NAME = "com.github.jcrd.lighten"


def new_db():
    p = Path(Path.home(), ".local", "share", "lighten")
    os.makedirs(p, exist_ok=True)
    return DB(str(Path(p, "lightend.db")))


class Service(dbus.service.Object):
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName(BUS_NAME, dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/com/github/jcrd/lighten")

        self.loop = GLib.MainLoop()
        self.debouncer = Debouncer(self.save)
        self.db = new_db()

    def run(self):
        logging.debug("Running...")
        self.loop.run()

    def save(self):
        logging.debug("Saving brightness...")
        value = ddcutil.get()
        if value:
            logging.debug("Brightness saved: %d", value)
            self.db.save(value)

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="u", out_signature="b")
    def set_brightness(self, value):
        r = ddcutil.set(value, absolute=True)
        self.debouncer.start()
        return r

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="i", out_signature="b")
    def add_brightness(self, value):
        r = ddcutil.set(value)
        self.debouncer.start()
        return r

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="", out_signature="b")
    def restore_brightness(self):
        b = self.db.get()
        if not b:
            return False
        self.set_brightness(b)
        logging.debug("Brightness restored: %d", b)
        return True


def main():
    if os.getenv("LIGHTEN_DEBUG"):
        logging.basicConfig(level=logging.DEBUG)
    Service().run()


if __name__ == "__main__":
    main()
