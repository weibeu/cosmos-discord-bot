from cosmos.core.cosmos import Cosmos

if __name__ == "__main__":
    bot = Cosmos()
    try:
        bot.eh.sentry.init(bot.configs.sentry.dsn)  # Initialise sentry integration.
    except bot.eh.sentry.utils.BadDsn:
        bot.log.error("Invalid sentry DSN provided.")
    bot.log.info(f"All initial tasks completed. [{bot.time.round_time()} seconds.]")
    bot.run()
