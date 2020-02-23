from .banner import WelcomeBanner
from .messages import WelcomeMessage


class Welcome(WelcomeBanner, WelcomeMessage):
    """A plugin to greet newly joined members in several ways."""
