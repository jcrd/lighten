import logging
import subprocess


def set(value, relative=False):
    cmd = ["ddcutil", "setvcp", "10"]
    if relative:
        sign = "+"
        if value < 0:
            sign = "-"
        cmd.append(sign)
    cmd.append(str(abs(value)))

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        logging.warning("Failed to set monitor brightness")
        return False


def get():
    try:
        r = subprocess.run(
            ["ddcutil", "getvcp", "-t", "10"], stdout=subprocess.PIPE, check=True
        )
        return int(r.stdout.split()[3])
    except subprocess.CalledProcessError:
        logging.warning("Failed to get monitor brightness")
        return None
