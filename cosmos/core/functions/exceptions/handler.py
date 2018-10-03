import sentry_sdk as sentry


class ExceptionHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.sentry = sentry
        try:
            self.sentry.init(self.bot.configs.sentry.dsn)
        except self.utils.BadDsn:
            self.bot.log.error("Invalid sentry DSN provided.")
