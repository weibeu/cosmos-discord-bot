from raven import Client


class ExceptionHandler(Client):

    def __init__(self, bot):
        self.bot = bot
        super().__init__(self.bot.configs.sentry.dsn)
