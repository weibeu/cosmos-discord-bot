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

from .roles import WelcomeRoles
from .banner import WelcomeBanner
from .messages import WelcomeMessage


class Welcome(WelcomeBanner, WelcomeMessage, WelcomeRoles):
    """A plugin to greet newly joined members using Welcome Messages and Banners.

    Welcome Message:
        A plugin to send customized welcome messages for newly joined members. Lets you set fully customized
        template to use for Welcome Messages using different variables. Use `{variable}` in your template to use the
        variables.
        If Welcome Banner is enabled, the Welcome Messages are included along with the welcome banners.

        Valid Variables:
            - {id} -- Discord ID of the member.
            - {mention} -- Mentions the member.
            - {name} -- Discord name of the member excluding their Discord discriminator.
            - {username} -- Discord name of the member including their Discord discriminator.
            - {discriminator} -- Discriminator of the member.

    Welcome Banner:
        A plugin to serve and manage customized static or animated GIF Welcome Banners.

    Welcome Roles:
        Assign roles to new members right after they join your server.

    """
