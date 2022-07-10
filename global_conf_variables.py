from config_parser import config_json_parser

config = config_json_parser()


class ConfigDict(dict):
    """
    creates a dictionary from jconfig.json

    Assumes shields are counted from maingate to tailgate
    Maximum of 4 sensor locations related to:
        - 1st Pulse
        - 2nd Pulse
        - 3rd Pulse
        - 4th Pulse

    dist_AtoB = config['dist_shield_AtoB']  # distance from shield A to B
    dist_BtoC = config['dist_shield_BtoC']  # distance from shield B to C
    dist_CtoD = config['dist_shield_CtoD']  # distance from shield C to D
    LW_face_area = config['LW_face_area']  # average area of the longwall face
    shield_width = config['shield_width']  # shield width

    # ventilation velocity (ventilation velocity assumption from event analyse 211204, 14/7/21)
    Vvent = config['vent_velocity']

    sensor_1 = config['sensor_loc_1']  # sensor location 1 on shield A
    sensor_2 = config['sensor_loc_2']  # sensor location 2 on shield B
    sensor_3 = config['sensor_loc_3']  # sensor location 3 on shield C
    sensor_4 = config['sensor_loc_4']  # sensor location 4 on shield D

    """
    def __init__(self):
        super().__init__()
        self.config = dict()

    def add(self, key, value):
        self[key] = value


dict_obj = ConfigDict()


def get_values():
    for key, value in config.items():
        dict_obj.add(key, value)
    return list(dict_obj.values())


def get_keys():
    for key, value in config.items():
        dict_obj.add(key, value)
    return list(dict_obj.keys())
