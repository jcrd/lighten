import time
from threading import Lock, Thread


class Debouncer:
    def __init__(self, interval=3):
        self.mutex = Lock()
        self.update_time = None
        self.running = False
        self.interval = interval

    def _target(self, callback):
        while True:
            self.mutex.acquire()
            try:
                t = time.time() - self.update_time
                if t >= self.interval:
                    self.running = False
            finally:
                self.mutex.release()
            if not self.running:
                callback()
                return
            time.sleep(self.interval)

    def start(self, callback):
        self.mutex.acquire()
        try:
            self.update_time = time.time()
            if self.running:
                return
            Thread(target=self._target, args=[callback], daemon=True).start()
            self.running = True
        finally:
            self.mutex.release()
