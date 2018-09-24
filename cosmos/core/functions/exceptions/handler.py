import sentry_sdk as sentry


class ExceptionHandler(sentry):

    def __init__(self, bot):
        self.bot = bot
        try:
            super().init(self.bot.configs.sentry.dsn)
        except self.utils.BadDsn:
            self.bot.log.error("Invalid sentry DSN provided.")
