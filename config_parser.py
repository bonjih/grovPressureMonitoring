import json

configs = {}


def config_json_parser():
    with open('./config.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        configs.update(data.items())
    return configs


def db_json_parser():
    db_field_key = []

    with open('./db_fields.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        for key, value in data.items():
            db_field_key.append(key)
    return db_field_key
