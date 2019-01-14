class GuildEmotes(object):

    def __init__(self, emotes: list):
        self.__emotes = emotes
        self.__set()

    def __set(self):
        for emote in self.__emotes:
            self.__setattr__(emote.name, emote)
