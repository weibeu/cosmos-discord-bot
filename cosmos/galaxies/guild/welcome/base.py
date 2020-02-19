from ..settings.base import Settings


class WelcomeBase(Settings):

    @Settings.group(name="welcome", aliases=["join"])
    async def welcome(self, ctx):
        """Manage different welcome settings of your server."""
        pass
