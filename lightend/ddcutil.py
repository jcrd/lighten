import logging
import subprocess
import sys


class ddcutil:
    def __init__(self):
        self.initial_brightness, self.max_brightness = self.get()

    def clamp_brightness(self, v):
        return max(0, min(v, self.max_brightness))

    def set(self, v):
        v = self.clamp_brightness(v)
        try:
            subprocess.run(["ddcutil", "setvcp", "10", str(v)], check=True)
            return True, v
        except subprocess.CalledProcessError:
            logging.warning("ddcutil: Failed to set monitor brightness")
            return False, v

    def get(self):
        """Return the current and max monitor brightness."""
        try:
            r = subprocess.run(
                ["ddcutil", "getvcp", "10"], stdout=subprocess.PIPE, check=True
            )
            s = r.stdout.split()
            return (int(s[-5].decode().strip(",")), int(s[-1]))
        except subprocess.CalledProcessError:
            logging.critical("ddcutil: Failed to get monitor brightness info")
            sys.exit(4)
