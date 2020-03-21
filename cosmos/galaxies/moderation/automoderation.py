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
    """An Auto Moderation plugin based on triggers and actions.
    Server Administrators can create different triggers and specify various actions for it. The bot responds and
    performs all of the actions which were specified for this trigger when a member violates its protocol. A single
    trigger can have multiple actions set.

    Available Triggers:
        - spoilers -- Triggers when a member sends any kind of spoiler content.
        - emoji_spam -- Triggers when there are lots of emotes in a single message.
        - banned_words -- Triggers when a message contains any of the banned or blacklisted words.
        - mass_mentions -- Triggers when there are lots of mentions in a single message.
        - discord_invites -- Triggers when a message contains invites to different discord servers.

    Available trigger Actions:
        - delete -- Deletes the message which invoked the trigger.
        - warn -- Warns the member who invoked the trigger.
        - mute -- Mutes the member who invoked the trigger by adding the muted role.
        - kick -- Kicks the member who invoked the trigger.
        - ban -- Bans the member who invoked the trigger.

    """

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author == self.bot.user:
            return

        # TODO: Ignore admins and moderators.

        guild_profile = await self.bot.guild_cache.get_profile(message.guild.id)

        trigger = guild_profile.auto_moderation.triggers.get("banned_words")
        if trigger:
            try:
                # if set(message.content.lower().split()) & trigger.words:
                if [word for word in trigger.words if word.lower() in message.content.lower()]:    # TODO: Use RE.
                    await trigger.dispatch(message=message, member=message.author)
            except AttributeError:
                pass    # No banned word set.

        trigger = guild_profile.auto_moderation.triggers.get("mass_mentions")
        if trigger:
            if len(message.mentions) + len(message.role_mentions) \
                    > self.plugin.data.auto_moderation.mass_mentions_count:
                await trigger.dispatch(message=message, member=message.author)

        trigger = guild_profile.auto_moderation.triggers.get("emoji_spam")
        if trigger:
            if self.bot.utilities.count_emojis(message.content) > self.plugin.data.auto_moderation.emoji_spam_count:
                await trigger.dispatch(message=message, member=message.author)

            # TODO: Consider multi line emoji spams as well.

        trigger = guild_profile.auto_moderation.triggers.get("discord_invites")
        if trigger:
            if self.bot.utilities.get_invites(message.content):
                await trigger.dispatch(message=message, member=message.author)

        trigger = guild_profile.auto_moderation.triggers.get("spoilers")
        if trigger:
            if [_ for _ in message.attachments if _.is_spoiler()]:    # TODO: Include spoiler || || regex.
                await trigger.dispatch(message=message, member=message.author)

    @Cog.group(name="triggers", aliases=["trigger", "violation", "violations"], invoke_without_command=True)
    async def triggers(self, ctx):
        """Displays all of the active triggers along with their actions."""
        guild_profile = await ctx.fetch_guild_profile()
        embed = ctx.embed_line(f"Triggers or Violations - Auto Moderation", ctx.guild.icon_url)
        embed.description = "```css\nDisplaying Triggers or Violations set in the server along with their actions " \
                            "which are automatically taken by the bot.```"
        if guild_profile.auto_moderation.triggers:
            for trigger in guild_profile.auto_moderation.triggers.values():
                embed.add_field(name=trigger.title, value="`ACTIONS:` " + ", ".join(trigger._actions))    # Ignore lint.
        else:
            embed.description = "❌    No auto moderation triggers or violations has been set yet."
        await ctx.send(embed=embed)

    @triggers.command(name="create", aliases=["set", "add"])
    async def create_trigger(self, ctx, trigger: TriggerConvertor, *actions: ActionConvertor):
        """Sets a new Auto Moderation trigger with specified actions."""
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.auto_moderation.create_trigger(trigger, actions)
        await ctx.send_line(f"✅    {trigger} auto moderation trigger or violation has been created.")

    @create_trigger.error
    async def create_trigger_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send_line(str(error))

    @triggers.command(name="remove", aliases=["delete"])
    async def remove_trigger(self, ctx, trigger: TriggerConvertor):
        """Removes specified Auto Moderation trigger."""
        guild_profile = await ctx.fetch_guild_profile()
        if trigger not in guild_profile.auto_moderation.triggers:
            return await ctx.send_line(f"❌    You haven't created that trigger yet.")
        await guild_profile.auto_moderation.remove_trigger(trigger)
        await ctx.send_line(f"✅    {trigger} auto moderation trigger or violation has been removed.")

    @Cog.group(name="banword", aliases=["bannedwords", "banwords"], invoke_without_command=True)
    async def ban_word(self, ctx, word=None):
        """Blacklists or bans specified word. To make it work, first set `banned_words` Auto Moderation trigger."""
        guild_profile = await ctx.fetch_guild_profile()
        trigger = guild_profile.auto_moderation.triggers.get("banned_words")
        if not trigger:
            return await ctx.send_line(f"❌    You haven't set banned_words trigger or violation yet.")
        if len(trigger.words) >= self.plugin.data.auto_moderation.max_banned_words:
            return await ctx.send_line("❌    Sorry, but you can't ban anymore words.")
        if not word:
            if not trigger.words:
                return await ctx.send_line(f"❌    You haven't banned any words yet.")
            embed = ctx.embeds.primary()
            embed.title = "List of banned words"
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            embed.description = "```css\nDisplaying banned or blacklisted words in the server.```\n"
            try:
                embed.description += f"{self.bot.emotes.misc.next} " + ", ".join(trigger.words) + "\n​\n"
            except AttributeError:
                embed.description = "❌    You haven't banned any words yet."
            # TODO: Provide, accept banned words file as well.
            return await ctx.send(embed=embed)
        await guild_profile.auto_moderation.ban_word(word)
        await ctx.send_line(f"✅    {word} has been added to list of banned words.")

    @ban_word.command(name="clear", aliases=["clean", "purge"])
    async def clear_banned_words(self, ctx):
        """Removes all of the currently blacklisted or banned words."""
        guild_profile = await ctx.fetch_guild_profile()
        if not await ctx.confirm():
            return
        trigger = guild_profile.auto_moderation.triggers.get("banned_words")
        if not trigger:
            return await ctx.send_line(f"❌    You haven't set {trigger.name} trigger or violation yet.")
        await guild_profile.auto_moderation.clear_banned_words()
        await ctx.send_line(f"✅    List of banned words in this server has been cleared.")

    # TODO: Command to set auto mute timer.
