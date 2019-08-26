import os
import re

from .api.hastebin import HasteBin


class Utils(HasteBin):

    @staticmethod
    def get_python_path(path):
        return f"{path.replace('/', '.')}"[:-3]

    @staticmethod
    def get_file_directory(path):
        return os.path.basename(os.path.dirname(path))

    @staticmethod
    def find_urls(string):
        return re.findall(r"(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?", string)

    @staticmethod
    def find_image_urls(string):
        return re.findall(r"(http(s?):)([/|.|\w|\s|-])*\.(?:jpg|gif|png)", string)

    def find_urls_and_strip(self, string):
        urls = self.find_urls(string)
        for url in urls:
            string.replace(url, str())
        return string, urls

    def find_image_urls_and_strip(self, string):
        urls = self.find_image_urls(string)
        for url in urls:
            string.replace(url, str())
        return string, urls

    @staticmethod
    def count_emojis(string):
        return len(re.findall(r"<(a?):([A-Za-z0-9_]+):([0-9]+)>", string))

    @staticmethod
    def get_invites(string):
        return re.findall(r"(?:https?://)?discord(?:app\.com/invite|\.gg)/?[a-zA-Z0-9]+/?", string)
