import time
from threading import Lock, Thread


class Debouncer:
    def __init__(self, callback, interval=3):
        self.mutex = Lock()
        self.update_time = None
        self.running = False
        self.callback = callback
        self.interval = interval

    def _target(self):
        while True:
            self.mutex.acquire()
            try:
                t = time.time() - self.update_time
                if t >= self.interval:
                    self.running = False
            finally:
                self.mutex.release()
            if not self.running:
                self.callback()
                return
            time.sleep(self.interval)

    def start(self):
        self.mutex.acquire()
        try:
            self.update_time = time.time()
            if self.running:
                return
            Thread(target=self._target).start()
            self.running = True
        finally:
            self.mutex.release()
