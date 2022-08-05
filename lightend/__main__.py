import configparser
import logging
import os
import sys
from pathlib import Path

from gi.repository import GLib

from lightend.service import Service


def check_key(section, key):
    if key not in section or section[key] == None:
        logging.critical(f"Sensor configuration requires '{key}' key")
        sys.exit(2)


def main():
    if os.getenv("LIGHTEN_DEBUG"):
        logging.basicConfig(level=logging.DEBUG)

    config = configparser.ConfigParser()
    config["params"] = {
        "save_fidelity": "5",
        "max_deviation": "10",
        "change_threshold": "20",
        "restore_interval": "1200",
    }

    p = Path(GLib.get_user_config_dir(), "lighten", "lightend.conf")
    if p.exists():
        logging.debug(f"Reading config: {p}")
        config.read(p)
    else:
        logging.critical(f"Config file not found: {p}")
        sys.exit(2)

    if "sensor" not in config:
        logging.critical("Sensor configuration not found")
        sys.exit(2)
    check_key(config["sensor"], "vendor_id")
    check_key(config["sensor"], "product_id")

    Service(config).run()


if __name__ == "__main__":
    main()
