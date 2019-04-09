from .base import Settings


class BannerSettings(Settings):

    @Settings.welcome.command(name="banner")
    async def welcome_banner(self, ctx):
        pass
