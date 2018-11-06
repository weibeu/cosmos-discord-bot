import json
import yaml


class FileHandler(object):

    def __init__(self, bot):
        self.bot = bot

    def get_file_data(self, path):
        try:
            file = open(path)
            if path.endswith(".json"):
                file_data = json.load(file)
            elif path.endswith(".yaml") or path.endswith(".yml"):
                file_data = yaml.load(file)
            else:
                self.bot.log.info(f"Unsupported file specified. Ignoring {path}.")
            return file_data    # dict
        except FileNotFoundError:
            print(f"Unable to find specified file '{path}'.")
            return
