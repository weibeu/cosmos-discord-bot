"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from cosmos import get_bot
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv(".env")
    bot = get_bot()
    try:
        bot.eh.sentry.init(**bot.configs.sentry.raw)  # Initialise sentry for deeper integration.
    except bot.eh.sentry.utils.BadDsn:
        bot.log.error("Invalid sentry DSN provided.")
    bot.log.info(f"All initial tasks completed. [{bot.time.round_time()} seconds.]")
    bot.run()
