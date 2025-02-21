import os, json

# Constants
CONFIG_FILE_PATH = "config/config.json"
BASE_CONFIG_DICT = {
        "Actions": {
            "Left": {
                "Closed_Fist": [],
                "Open_Palm": [],
                "Pointing_Up": [],
                "Thumb_Down": [],
                "Thumb_Up": [],
                "Victory": [],
                "ILoveYou": []
            },
            "Right": {
                "Closed_Fist": [],
                "Open_Palm": [],
                "Pointing_Up": [],
                "Thumb_Down": [],
                "Thumb_Up": [],
                "Victory": [],
                "ILoveYou": []
            }
        },
        "Settings": {
            "COMBINATION_MODE": False,
            "PRESS_RELEASE_WAIT_TIME": 0.1,
            "ACTION_COOLDOWN": 1.0
        }
    }

# Custom exception class for handling configuration file validation errors
class ValidationError(Exception):
    pass

# Returns True if the configuration file exists, can be opened and its structure is correct; otherwise, returns False
def check():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = json.load(file)
            
            # Check if first-level keys are correct in the configuration file
            if BASE_CONFIG_DICT.keys() != config.keys():
                raise ValidationError
            
            # Iterate over first-level keys
            for key in BASE_CONFIG_DICT.keys():
                # Check if second-level keys inside the current first-level key are correct in the configuration file
                if BASE_CONFIG_DICT[key].keys() != config[key].keys():
                    raise ValidationError
                
                # Iterate over second-level keys inside the current first-level key
                for subkey in BASE_CONFIG_DICT[key].keys():
                    # When second-level key value type is not dictionary
                    if not isinstance(BASE_CONFIG_DICT[key][subkey], dict):
                        # Check if current second-level key value type is correct in the configuration file
                        if type(BASE_CONFIG_DICT[key][subkey]) != type(config[key][subkey]):
                            raise ValidationError
                        
                        # Check that certain numeric values from keys under Settings are positive
                        if key == "Settings" and (subkey == "PRESS_RELEASE_WAIT_TIME" or subkey == "ACTION_COOLDOWN"):
                            if config[key][subkey] < 0:
                                raise ValidationError
                    else:
                        # Check if third-level keys inside the current second-level key are correct in the configuration file
                        if BASE_CONFIG_DICT[key][subkey].keys() != config[key][subkey].keys():
                            raise ValidationError
                        
                        # Iterate over third-level keys inside the current second-level key
                        for third_lvl_key in BASE_CONFIG_DICT[key][subkey].keys():
                            # Check if current third-level key value type is correct in the configuration file
                            if type(BASE_CONFIG_DICT[key][subkey][third_lvl_key]) != type(config[key][subkey][third_lvl_key]):
                                raise ValidationError
                            
                            # Check that the items inside each action list are of String type
                            if key == "Actions":
                                for item in config[key][subkey][third_lvl_key]:
                                    if not isinstance(item, str):
                                        raise ValidationError
            
            return True
    except (FileNotFoundError, OSError, json.JSONDecodeError, AttributeError, ValidationError):
        return False

# Creates the configuration JSON file and returns True if the write has been done, or False otherwise
def create():
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        
        with open(CONFIG_FILE_PATH, 'w') as file:
            json.dump(BASE_CONFIG_DICT, file, indent=4)
            
            return True
    except OSError:
        return False

# Returns an array containing the action for a particular hand gesture or, if an error happens, an empty array
def retrieve_action(hand, gesture):
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = json.load(file)
            
            action = config["Actions"][hand][gesture]
            
            if not isinstance(action, list):
                raise ValidationError
            
            for item in action:
                if not isinstance(item, str):
                    raise ValidationError
                
            return action
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, ValidationError):
        return []
    
# Returns a dictionary containing the application settings or, if an error happens, a dictionary containing the default settings
def retrieve_settings():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = json.load(file)
            
            settings = config["Settings"]

            if BASE_CONFIG_DICT["Settings"].keys() != settings.keys():
                raise ValidationError
            
            for key in BASE_CONFIG_DICT["Settings"].keys():
                if type(BASE_CONFIG_DICT["Settings"][key]) != type(settings[key]):
                    raise ValidationError
                
                if (key == "PRESS_RELEASE_WAIT_TIME" or key == "ACTION_COOLDOWN") and settings[key] < 0:
                    raise ValidationError
            
            return settings
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, ValidationError):
        return BASE_CONFIG_DICT["Settings"]
    
# Returns a dictionary containing the whole application configuration or False if an error happens
def retrieve_configuration():
    try:
        with open(CONFIG_FILE_PATH, 'r') as file:
            config = json.load(file)
            
            return config
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return False
    
# Saves the action for a particular hand gesture, checking if the configuration file needs to be created before doing so, and returns True if the new action has
# been correctly written, or False otherwise
def save_action(hand, gesture, action):
    if not check() and not create():
        return False
        
    try:
        with open(CONFIG_FILE_PATH, 'r+') as file:
            config = json.load(file)
            config["Actions"][hand][gesture] = action
            
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()

            return True
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError):
        return False
    
# Saves the application settings, checking if the configuration file needs to be created before doing so, and returns True if the new action has been correctly
# written, or False otherwise
def save_settings(settings):
    if not check() and not create():
        return False
        
    try:
        with open(CONFIG_FILE_PATH, 'r+') as file:
            config = json.load(file)
            config["Settings"] = settings
            
            file.seek(0)
            json.dump(config, file, indent=4)
            file.truncate()

            return True
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError):
        return False