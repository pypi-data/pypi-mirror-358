import configparser
import os

def get_mode_serius():
    config = configparser.ConfigParser()
    cfg_path = ".kalkulator_ngaco.cfg"
    if not os.path.exists(cfg_path):
        return False
    config.read(cfg_path)
    return config.get("mode", "serius", fallback="off").lower() == "on"	
