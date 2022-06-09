import subprocess


def set(value, absolute=False):
    cmd = ["ddcutil", "setvcp", "10"]
    if not absolute:
        sign = "+"
        if value < 0:
            sign = "-"
        cmd.append(sign)
    cmd.append(str(abs(value)))

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get():
    try:
        r = subprocess.run(
            ["ddcutil", "getvcp", "-t", "10"], stdout=subprocess.PIPE, check=True
        )
        return int(r.stdout.split()[3])
    except subprocess.CalledProcessError:
        return None
