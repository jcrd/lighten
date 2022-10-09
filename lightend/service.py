import logging
import os
from pathlib import Path

from gi.repository import Gio, GLib

import lightend.ddcutil as ddcutil
from lightend.database import DB
from lightend.debouncer import Debouncer
from lightend.hid_source import HIDSource
from lightend.restorer import Restorer

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
      <method name='NormalizeBrightness'>
          <arg name='success' type='b' direction='out'/>
      </method>
      <method name='ToggleAuto'>
          <arg name='on' type='b' direction='out'/>
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


def rounder(n, x=5):
    if n % 10 >= x:
        return int((n + 10) / 10) * 10
    else:
        return int(n / 10) * 10


normalize_methods = {
    "exact": lambda n: n,
    "round": rounder,
    "round-up": lambda n: rounder(n, x=1),
    "round-down": lambda n: rounder(n, x=9),
}


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
        self.data = None
        self.brightness = None
        self.owner_id = None
        self.hid_source = None
        self.change_countdown = 0
        self.auto = True

        params = config["params"]

        self.node = Gio.DBusNodeInfo.new_for_xml(xml)
        self.loop = GLib.MainLoop()
        self.debouncer = Debouncer()
        self.db = new_db(int(params["save_fidelity"]))

        self.hid_source = HIDSource(
            cast_id(config["sensor"]["vendor_id"]),
            cast_id(config["sensor"]["product_id"]),
        )
        self.hid_source.set_callback(self.hid_callback)
        self.hid_source.attach()

        self.max_deviation = int(params["max_deviation"])
        self.change_threshold = int(params["change_threshold"])
        self.change_rate = int(params["change_rate"])
        self.normalize_method = normalize_methods[params["normalize_method"]]

        self.restorer = Restorer(
            self,
            # Convert to milliseconds for `timeout_add`.
            int(params["restore_interval"]) * 1000,
            int(params["restore_range"]),
            True if params["auto_normalize"].lower() == "true" else False,
            self.hid_source.connect,
        )

        self.owner_id = Gio.bus_own_name(
            Gio.BusType.SESSION,
            BUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            self.on_bus_acquired,
            None,
            None,
        )

    def __del__(self):
        if self.owner_id:
            Gio.bus_unown_name(self.owner_id)

    def detect_change(self, data):
        return abs(data - self.data) >= self.change_threshold

    def hid_callback(self, data):
        if self.change_countdown > 0:
            self.change_countdown -= 1
            return True
        last_data = self.data
        self.data = data
        # Schedule restore after receiving first data.
        if last_data is None:
            self.restorer.handle_brightness()
            self.restorer.schedule()
        elif self.detect_change(last_data):
            logging.debug("Sensor change detected...")
            if self.restore_brightness():
                self.change_countdown = self.change_rate
        return True

    def run(self):
        logging.debug("Running...")
        self.brightness = ddcutil.get()
        self.loop.run()

    def save(self, data):
        if self.brightness is not None:
            self.db.save(data, self.brightness)

    def debounce_save(self):
        logging.debug("Debouncing brightness save...")
        self.debouncer.start(lambda d=self.data: self.save(d))

    def restore_brightness(self, method=False):
        if not method and not self.auto:
            return False
        b = self.db.get(self.data, self.max_deviation)
        if b is None or b == self.brightness:
            return False
        r = ddcutil.set(b)
        if r:
            self.brightness = b
            logging.debug("Brightness restored: (%d, %d)", self.data, b)
        return r

    def normalize_brightness(self, method=False):
        if not method and not self.auto:
            return False
        d = self.normalize_method(self.data)
        r = ddcutil.set(d)
        if r:
            self.brightness = d
            logging.debug("Brightness normalized: (%d, %d)", self.data, d)
            self.debounce_save()
        return r

    def toggle_auto(self):
        self.auto = not self.auto
        logging.debug("Toggled auto adjustment: %s", "on" if self.auto else "off")
        return self.auto

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

    def on_handle_backlight(self, conn, sender, path, iname, method, args, invo):
        if method == "SetBrightness":
            v = args.unpack()[0]
            r = ddcutil.set(v)
            self.brightness = v
            self.debounce_save()
            return_bool(invo, r)
        elif method == "AddBrightness":
            v = args.unpack()[0]
            r = ddcutil.set(v, relative=True)
            self.brightness += v
            self.debounce_save()
            return_bool(invo, r)
        elif method == "RestoreBrightness":
            return_bool(invo, self.restore_brightness(method=True))
        elif method == "NormalizeBrightness":
            return_bool(invo, self.normalize_brightness(method=True))
        elif method == "ToggleAuto":
            return_bool(invo, self.toggle_auto())
        elif method == "GetBrightness":
            return_int(invo, self.brightness)

    def on_handle_sensor(self, conn, sender, path, iname, method, args, invo):
        if method == "GetData":
            return_int(invo, self.data)
