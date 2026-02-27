import json
import os
from . import constants

DEFAULT_CONFIG = {
    "library_path": "C:\\MyKitbashLibrary",
    "auto_scale": True,
    "auto_conform": True
}

def load_config():
    
    if os.path.exists(constants.CONFIG_PATH):
        try:
            with open(constants.CONFIG_PATH, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(data):
    
    try:
        with open(constants.CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False