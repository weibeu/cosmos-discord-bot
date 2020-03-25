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
