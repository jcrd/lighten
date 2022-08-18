import logging

from gi.repository import Gio, GLib

LOGIND_NAME = "org.freedesktop.login1"
LOGIND_IFACE = f"{LOGIND_NAME}.Manager"
LOGIND_PATH = "/org/freedesktop/login1"


class Restorer:
    def __init__(self, service, i, r):
        self.service = service
        self.interval = i
        self.range = r
        self.range_count = r
        self.range_data = None
        self.data = None

        self.logind = Gio.DBusProxy.new_sync(
            Gio.bus_get_sync(Gio.BusType.SYSTEM, None),
            Gio.DBusProxyFlags.NONE,
            None,
            LOGIND_NAME,
            LOGIND_PATH,
            LOGIND_IFACE,
            None,
        )
        self.logind.connect("g-signal", self.on_logind_signal)

    def restore_range(self):
        logging.debug("Restore range reached")
        if self.service.detect_change(self.range_data):
            self.service.restore_brightness()
        else:
            logging.debug(
                f"No change detected: {self.range_data} -> {self.service.data}"
            )

    def timeout(self):
        logging.debug("Restore timeout reached")
        self.range_count -= 1

        if self.range_count == 0:
            self.range_count = self.range
            self.restore_range()
        elif self.service.detect_change(self.data):
            self.service.restore_brightness()
        else:
            logging.debug(f"No change detected: {self.data} -> {self.service.data}")

        self.schedule()

    def schedule(self):
        self.data = self.service.data
        if self.range_count == self.range:
            self.range_data = self.data
        self.source = GLib.timeout_add(self.interval, self.timeout)

    def on_logind_signal(self, conn, sender, signal, args):
        if signal != "PrepareForSleep":
            return
        logging.debug(f"logind signal received: PrepareForSleep ({args.unpack()[0]})")
        self.service.restore_brightness()
        if self.source:
            GLib.source_remove(self.source)
            self.schedule()
