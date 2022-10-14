import logging
import sys

import hid


class Sensor:
    def __init__(self, vid, pid, size=16):
        super().__init__()
        self.vid = vid
        self.pid = pid
        self.size = size
        self.device = None

        self.connect()

    def __del__(self):
        super().__del__()
        if self.device:
            self.device.close()

    def connect(self):
        if self.device:
            self.device.close()
        try:
            self.device = hid.Device(self.vid, self.pid)
        except hid.HIDException as e:
            logging.critical(f"HID device (ID {self.vid:02x}:{self.pid:02x}): {e}")
            sys.exit(2)

    def get_data(self):
        try:
            data = self.device.get_input_report(0, self.size)
        except hid.HIDException as e:
            logging.critical(f"HID device: {e}")
            sys.exit(3)

        if not data:
            return (0, False)
        try:
            # Exclude report ID in first byte.
            data = int(data[1:].decode())
        except ValueError:
            return (0, False)

        if data == -1:
            logging.critical("HID device: sensor not found")
            sys.exit(1)
        if data == -2:
            logging.warning("HID device: invalid sensor data")
            # Try reconnecting if invalid data is received.
            self.connect()
            return (0, False)

        return (data, True)
