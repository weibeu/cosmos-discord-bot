import sentry_sdk as sentry


class ExceptionHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.sentry = sentry
