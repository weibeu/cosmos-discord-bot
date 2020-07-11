from .api import HasteBin

import os
import re

import random
import string as strings


SPOILER_RE = re.compile(r"(\|\|.+?\|\|)", re.DOTALL)
INVITE_RE = re.compile(
    r"(?:discord(?:[\.,]|dot)gg|"                     # Could be discord.gg/
    r"discord(?:[\.,]|dot)com(?:\/|slash)invite|"     # or discord.com/invite/
    r"discordapp(?:[\.,]|dot)com(?:\/|slash)invite|"  # or discordapp.com/invite/
    r"discord(?:[\.,]|dot)me|"                        # or discord.me
    r"discord(?:[\.,]|dot)io"                         # or discord.io.
    r")(?:[\/]|slash)"                                # / or 'slash'
    r"([a-zA-Z0-9]+)",                                # the invite code itself
    flags=re.IGNORECASE)


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
        return re.findall(r"(?:http:|https:)?//.*\.(?:png|jpg|gif)", string)

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
        return INVITE_RE.findall(string)

    @staticmethod
    def get_random_strings(length):
        return str().join(random.choices(strings.ascii_letters + strings.digits, k=length))

    @staticmethod
    def is_spoiler(string):
        return bool(SPOILER_RE.search(string))

    # @staticmethod
    # def humanize_stats(value, start=1000):
    #     if value >= start:
    #         return humanize.naturalsize(value, gnu=True)
    #     return value

    def get_random_elements(self, iterable, elements=1):
        try:
            return random.sample(iterable, elements)
        except ValueError:
            elements -= 1
            if not elements:
                return []
            return self.get_random_elements(iterable, elements - 1)
