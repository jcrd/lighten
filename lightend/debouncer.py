from gi.repository import GLib


class Debouncer:
    def __init__(self, interval=3):
        self.interval = interval * 1000
        self.source = None

    def start(self, callback):
        def _cb():
            if self.source:
                GLib.source_remove(self.source)
            callback()
        self.source = GLib.timeout_add(self.interval, _cb)
