import configparser
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
from lightend.hid_source import HIDSource

BUS_NAME = "com.github.jcrd.lighten"


def cast_id(i):
    return int(f"0x{i}", 16)


def new_db(save_fidelity):
    p = Path(Path.home(), ".local", "share", "lighten")
    os.makedirs(p, exist_ok=True)
    return DB(str(Path(p, "lightend.db")), save_fidelity)


class Service(dbus.service.Object):
    def __init__(self, config):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus_name = dbus.service.BusName(BUS_NAME, dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/com/github/jcrd/lighten")

        self.max_deviation = int(config["params"]["max_deviation"])
        self.change_threshold = int(config["params"]["change_threshold"])

        self.loop = GLib.MainLoop()
        self.debouncer = Debouncer()
        self.db = new_db(int(config["params"]["save_fidelity"]))

        self.hid_source = HIDSource(
            cast_id(config["device"]["vendor_id"]),
            cast_id(config["device"]["product_id"]),
        )
        self.hid_source.set_callback(self.hid_callback)
        self.hid_source.attach()

        self.data = None

    def hid_callback(self, data):
        last_data = self.data
        self.data = data
        if last_data and abs(last_data - data) > self.change_threshold:
            logging.debug("Sensor change detected...")
            self.restore_brightness()
        return True

    def run(self):
        logging.debug("Running...")
        self.loop.run()

    def save(self, data):
        v = ddcutil.get()
        if v is None:
            logging.warning("Failed to get monitor brightness")
            return
        self.db.save(data, v)

    def debounce_save(self):
        logging.debug("Debouncing brightness save...")
        self.debouncer.start(lambda d=self.data: self.save(d))

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="u", out_signature="b")
    def set_brightness(self, value):
        r = ddcutil.set(value, absolute=True)
        self.debounce_save()
        return r

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="i", out_signature="b")
    def add_brightness(self, value):
        r = ddcutil.set(value)
        self.debounce_save()
        return r

    @dbus.service.method(BUS_NAME + ".Backlight", in_signature="", out_signature="b")
    def restore_brightness(self):
        b = self.db.get(self.data, self.max_deviation)
        if not b:
            return False
        ddcutil.set(b, absolute=True)
        logging.debug("Brightness restored: (%d, %d)", self.data, b)
        return True


def main():
    if os.getenv("LIGHTEN_DEBUG"):
        logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config["params"] = {
        "save_fidelity": "5",
        "max_deviation": "10",
        "change_threshold": "20",
        "restore_interval": "1200",
    }

    p = Path(GLib.get_user_config_dir(), "lighten", "lightend.conf")
    if p.exists():
        logging.debug(f"Reading config: {p}")
        config.read(p)

    Service(config).run()


if __name__ == "__main__":
    main()
