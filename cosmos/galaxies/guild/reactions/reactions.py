from ..settings.base import Settings


class Reactions(Settings):
    """This plugin provides reaction based utilities."""

    @Settings.group(name="reaction", aliases=["reactions"])
    async def reaction(self, ctx):
        """It contains multiple reaction based sub-commands."""
        pass
