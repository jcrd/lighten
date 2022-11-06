import logging
import subprocess


class GetException(Exception):
    pass


def set(value):
    try:
        subprocess.run(["ddcutil", "setvcp", "10", str(value)], check=True)
        return True
    except subprocess.CalledProcessError:
        logging.warning("ddcutil: Failed to set monitor brightness")
        return False


def get():
    """Return the current and max monitor brightness."""
    try:
        r = subprocess.run(
            ["ddcutil", "getvcp", "10"], stdout=subprocess.PIPE, check=True
        )
        s = r.stdout.split()
        return (int(s[-5].decode().strip(",")), int(s[-1]))
    except subprocess.CalledProcessError:
        raise GetException
