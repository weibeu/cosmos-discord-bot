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

from discord.ext import commands


class NotPrime(commands.CheckFailure):

    message = "Click here to get prime and unlock all features including this."

    def __init__(self, message=str()):
        self.message = message or self.message


class GuildNotPrime(NotPrime):

    ...


class UserNotPrime(NotPrime):

    ...


class DisabledFunctionError(commands.CheckFailure):

    def __init__(self, globally=False):
        self.globally = globally


class CosmosIsDisableError(commands.CheckFailure):

    ...
