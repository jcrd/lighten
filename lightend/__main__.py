import configparser
import logging
import os
from pathlib import Path

from gi.repository import GLib

from lightend.service import Service


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

    Service(config).run()


if __name__ == "__main__":
    main()
