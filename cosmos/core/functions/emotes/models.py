class GuildEmotes(object):

    def __init__(self, emotes: list):
        self.emotes = emotes
        self.__set()

    def __set(self):
        for emote in self.emotes:
            self.__setattr__(emote.name, emote)
            # TODO: Mind unwanted memory consumptions.
