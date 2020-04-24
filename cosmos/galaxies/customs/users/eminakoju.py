from ... import Cog


class EminaKoju(Cog):

    __USER_ID = 394407882675978253

    @Cog.group(name="summon")
    @Cog.checks.check_user(__USER_ID)
    async def summon(self, ctx):
        pass

    @summon.command(name="mlbb", aliases=["ml", "MLBB"])
    async def summon_mlbb(self, ctx):
        to_summon = [
            331793750273687553, 250900865446182922, 463202259149258764, 332491715376054274, 517301933682327573,
            377756783130968064, 431890861278887947, 164676584756740096, 239099656330674178,
        ]
        content = " ".join([f"<@{user_id}>" for user_id in to_summon])
        await ctx.send(content)
