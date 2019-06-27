from .models.automoderation import triggers

from .. import Cog

from discord.ext import commands


class ActionConvertor(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return getattr(triggers.AutoModerationActions, argument.lower()).__name__
        except AttributeError:
            raise commands.BadArgument(f"❌    Action {argument} isn't supported yet.")


class TriggerConvertor(commands.Converter):

    async def convert(self, ctx, argument):
        if argument.lower() not in triggers.__triggers__:
            raise commands.BadArgument(f"❌    Trigger or violation {argument} isn't supported yet.")
        return argument.lower()


class AutoModeration(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @Cog.listener()
    async def on_message(self, message):
        guild_profile = await self.bot.guild_cache.get_profile(message.guild.id)

        trigger = guild_profile.auto_moderation.triggers.get("banned_words")
        try:
            if set(message.content.lower().split()) & trigger.words:
                await trigger.dispatch(message=message)
        except AttributeError:
            pass    # No banned word set.

    @Cog.group(name="triggers", aliases=["trigger", "violation", "violations"], invoke_without_command=True)
    async def triggers(self, ctx):
        guild_profile = await ctx.fetch_guild_profile()
        embed = ctx.embed_line(f"Active auto moderation triggers or violations", ctx.guild.icon_url)
        if guild_profile.auto_moderation.triggers:
            embed.description = ", ".join(
                [trigger.title for trigger in guild_profile.auto_moderation.triggers.values()]
            )
        else:
            embed.description = "❌    No auto moderation triggers or violations has been set yet."
        await ctx.send(embed=embed)

    @triggers.command(name="create", aliases=["set", "add"])
    async def create_trigger(self, ctx, trigger: TriggerConvertor, *actions: ActionConvertor):
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.auto_moderation.create_trigger(trigger, actions)
        await ctx.send_line(f"✅    {trigger} auto moderation trigger or violation has been created.")

    @create_trigger.error
    async def create_trigger_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send_line(str(error))

    @triggers.command(name="remove", aliases=["delete"])
    async def remove_trigger(self, ctx, trigger: TriggerConvertor):
        guild_profile = await ctx.fetch_guild_profile()
        if trigger not in guild_profile.auto_moderation.triggers:
            return await ctx.send_line(f"❌    You haven't created that trigger yet.")
        await guild_profile.auto_moderation.remove_trigger(trigger)
        await ctx.send_line(f"✅    {trigger} auto moderation trigger or violation has been removed.")

    @Cog.group(name="banword", aliases=["bannedwords", "banwords"], invoke_without_command=True)
    async def ban_word(self, ctx, word=None):
        guild_profile = await ctx.fetch_guild_profile()
        trigger = guild_profile.auto_moderation.triggers.get("banned_words")
        if not trigger:
            return await ctx.send_line(f"❌    You haven't set {trigger.name} trigger or violation yet.")
        if not word:
            embed = ctx.embed_line(f"List of banned words in {ctx.guild.name}", ctx.guild.icon_url)
            try:
                embed.description = ", ".join(trigger.words)
            except AttributeError:
                embed.description = "❌    No words banned yet."
            return await ctx.send(embed=embed)
        await guild_profile.auto_moderation.ban_word(word.lower())
        await ctx.send_line(f"✅    {word} has been added to list of banned words.")

    @ban_word.command(name="clear", aliases=["clean", "purge"])
    async def clear_banned_words(self, ctx):
        guild_profile = await ctx.fetch_guild_profile()
        trigger = guild_profile.auto_moderation.triggers.get("banned_words")
        if not trigger:
            return await ctx.send_line(f"❌    You haven't set {trigger.name} trigger or violation yet.")
        await guild_profile.clear_banned_words()
        await ctx.send_line(f"✅    List of banned words in this server has been cleared.")
