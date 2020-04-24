from ...functions import Cog


class CosmosInformation(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    @Cog.command(name="vote")
    async def vote_cosmos(self, ctx):
        """Love Cosmos? Help others find it by voting Cosmos on top.gg bot page <3."""
        res = "Click here to vote Cosmos on top.gg <3."
        await ctx.send_line(res, icon_url=self.bot.theme.images.heart, author_url=self.bot.configs.info.top_vote_page)
