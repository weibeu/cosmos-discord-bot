import json

import yaml


class FileHandler(object):

    @staticmethod
    def get_file_data(path):
        file_data = dict()
        file = open(path)
        if path.endswith(".json"):
            file_data = json.load(file)
        elif path.endswith(".yaml") or path.endswith(".yml"):
            file_data = yaml.safe_load(file)
        else:
            pass
        return file_data  # dict
