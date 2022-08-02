import logging
import sys

import hid
from gi.repository import GLib


class HIDSource(GLib.Source):
    def __init__(self, vid, pid, size=64):
        super().__init__()
        self.size = size
        self.device = None

        try:
            self.device = hid.Device(vid, pid)
        except hid.HIDException as e:
            logging.critical(f"HID device (ID {vid:02x}:{pid:02x}): {e}")
            sys.exit(2)

    def __del__(self):
        super().__del__()
        if self.device:
            self.device.close()

    def prepare(self):
        r = self.device.read(self.size)
        if not r:
            return False
        r = int(float(r.decode()))

        if r == -1:
            logging.critical("HID device: sensor not found")
            sys.exit(1)
        if r == -2:
            logging.warning("HID device: invalid sensor data")
            return False

        self.data = r
        return (True, -1)

    def dispatch(self, callback, _):
        return callback(self.data)
