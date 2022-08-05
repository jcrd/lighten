import logging
import os
from pathlib import Path

from gi.repository import Gio, GLib

import lightend.ddcutil as ddcutil
from lightend.database import DB
from lightend.debouncer import Debouncer
from lightend.hid_source import HIDSource

BUS_NAME = "com.github.jcrd.lighten"

xml = f"""
<node>
  <interface name='{BUS_NAME}.Backlight'>
      <method name='SetBrightness'>
          <arg name='value' type='u' direction='in'/>
          <arg name='success' type='b' direction='out'/>
      </method>
      <method name='AddBrightness'>
          <arg name='value' type='i' direction='in'/>
          <arg name='success' type='b' direction='out'/>
      </method>
      <method name='RestoreBrightness'>
          <arg name='success' type='b' direction='out'/>
      </method>
      <method name='GetBrightness'>
          <arg name='value' type='i' direction='out'/>
      </method>
  </interface>
  <interface name='{BUS_NAME}.Sensor'>
      <method name='GetData'>
          <arg name='value' type='i' direction='out'/>
      </method>
  </interface>
</node>
"""


def cast_id(i):
    return int(f"0x{i}", 16)


def new_db(save_fidelity):
    p = Path(Path.home(), ".local", "share", "lighten")
    os.makedirs(p, exist_ok=True)
    return DB(str(Path(p, "lightend.db")), save_fidelity)


def return_bool(invo, b):
    invo.return_value(GLib.Variant("(b)", (b,)))


def return_int(invo, i):
    invo.return_value(GLib.Variant("(i)", (-1 if i is None else i,)))


class Service:
    def __init__(self, config):
        self.node = Gio.DBusNodeInfo.new_for_xml(xml)
        self.loop = GLib.MainLoop()
        self.debouncer = Debouncer()
        self.db = new_db(int(config["params"]["save_fidelity"]))

        self.hid_source = HIDSource(
            cast_id(config["device"]["vendor_id"]),
            cast_id(config["device"]["product_id"]),
        )
        self.hid_source.set_callback(self.hid_callback)
        self.hid_source.attach()

        self.max_deviation = int(config["params"]["max_deviation"])
        self.change_threshold = int(config["params"]["change_threshold"])

        self.data = None

        self.owner_id = Gio.bus_own_name(
            Gio.BusType.SESSION,
            BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            self.on_bus_acquired,
            self.on_name_pass,
            self.on_name_pass,
        )

    def __del__(self):
        Gio.bus_unown_name(self.owner_id)

    def hid_callback(self, data):
        last_data = self.data
        self.data = data
        if last_data is not None and abs(last_data - data) > self.change_threshold:
            logging.debug("Sensor change detected...")
            self.restore_brightness()
        return True

    def run(self):
        logging.debug("Running...")
        self.loop.run()

    def get_brightness(self):
        v = ddcutil.get()
        if v is None:
            logging.warning("Failed to get monitor brightness")
        return v

    def save(self, data):
        v = self.get_brightness()
        if v:
            self.db.save(data, v)

    def debounce_save(self):
        logging.debug("Debouncing brightness save...")
        self.debouncer.start(lambda d=self.data: self.save(d))

    def on_bus_acquired(self, conn, name):
        conn.register_object(
            "/com/github/jcrd/lighten",
            self.node.interfaces[0],
            self.on_handle_backlight,
            None,
            None,
        )
        conn.register_object(
            "/com/github/jcrd/lighten",
            self.node.interfaces[1],
            self.on_handle_sensor,
            None,
            None,
        )

    def on_name_pass(self, conn, name):
        pass

    def on_handle_backlight(self, conn, sender, path, iname, method, args, invo):
        if method == "SetBrightness":
            r = ddcutil.set(args.unpack()[0], absolute=True)
            self.debounce_save()
            return_bool(invo, r)
        elif method == "AddBrightness":
            r = ddcutil.set(args.unpack()[0])
            self.debounce_save()
            return_bool(invo, r)
        elif method == "RestoreBrightness":
            b = self.db.get(self.data, self.max_deviation)
            r = b is not None
            if r:
                ddcutil.set(b, absolute=True)
                logging.debug("Brightness restored: (%d, %d)", self.data, b)
            return_bool(invo, r)
        elif method == "GetBrightness":
            return_int(invo, self.get_brightness())

    def on_handle_sensor(self, conn, sender, path, iname, method, args, invo):
        if method == "GetData":
            return_int(invo, self.data)
