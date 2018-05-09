import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils import db
from cogs.utils.paginator import Pages
from cogs.utils.util import get_random_embed_color, tick
from collections import Counter

class Prefix(commands.Converter):
    async def convert(self, ctx, argument):
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument('That is a reserved prefix already in use.')
        return argument

class Guild(object):
    """Guild commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def nicks(self, ctx, *, user:discord.User = None):
        """Displays past Nicknames of user since bot was added on guild."""
        if user is None:
            nicks = await db.get_nicks(ctx.guild.id, ctx.author.id)
            if nicks == []:
                await ctx.send("This user has no recorded nicknames.")
                return
            p = Pages(ctx, entries=nicks, per_page=7)
            await p.paginate()
        else:
            nicks = await db.get_nicks(ctx.guild.id, user.id)
            if nicks == []:
                await ctx.send("This user has no recorded nicknames.")
                return
            p = Pages(ctx, entries=nicks, per_page=7)
            await p.paginate()

    @commands.command()
    @commands.guild_only()
    async def usernames(self, ctx, *, user:discord.User = None):
        """Displays past Usernames of user since bot was added on guild."""
        if user is None:
            usernames = await db.get_usernames(ctx.guild.id, ctx.author.id)
            if usernames == []:
                await ctx.send("This user has no recorded usernames.")
                return
            p = Pages(ctx, entries=usernames, per_page=7)
            await p.paginate()
        else:
            usernames = await db.get_nicks(ctx.guild.id, user.id)
            if usernames == []:
                await ctx.send("This user has no recorded usernames.")
                return
            p = Pages(ctx, entries=nicks, per_page=7)
            await p.paginate()

    async def on_member_update(self, before, after):
        if before.nick != after.nick: #nick was changed
            nicks = await db.get_nicks(before.guild.id, before.id)
            if before.nick not in nicks and before.nick is not None:
                await db.dump_nick(after.guild.id, after.id, before.nick)
            elif after.nick not in nicks and after.nick is not None:
                await db.dump_nick(after.guild.id, after.id, after.nick)
        elif before.name != after.name: #username was changed
            usernames = await db.get_usernames(before.guild.id, before.id)
            if before.name not in usernames:
                await db.dump_username(after.guild.id, after.id, before.name)
            elif after.name not in usernames:
                await db.dump_username(after.guild.id, after.id, after.name)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def info(self, ctx, *, member: discord.Member = None):
        """Shows info about a member.
        This cannot be used in private messages. If you don't specify
        a member then the info returned will be yours.
        """

        if member is None:
            member = ctx.author

        e = discord.Embed()
        roles = [role.name.replace('@', '@\u200b') for role in member.roles]
        shared = sum(1 for m in self.bot.get_all_members() if m.id == member.id)
        voice = member.voice
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
        else:
            voice = 'Not connected.'

        e.set_author(name=str(member))
        e.set_footer(text='Member since').timestamp = member.joined_at
        e.add_field(name='ID', value=member.id)
        e.add_field(name='Servers', value=f'{shared} shared')
        e.add_field(name='Created', value=member.created_at)
        e.add_field(name='Voice', value=voice)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        nicks = await db.get_nicks(ctx.guild.id, member.id)
        if nicks != []:
            s = ''
            for nick in nicks:
                if nicks[-1] != nick:
                    s += nick+", "
                else:
                    s += nick
            e.add_field(name='Nicks', value=s)
        usernames = await db.get_usernames(ctx.guild.id, member.id)
        if usernames != []:
            s = ''
            for username in usernames:
                if usernames[-1] != username:
                    s += username+", "
                else:
                    s += username
            e.add_field(name='Usernames', value=s)
        if member.avatar:
            e.set_thumbnail(url=member.avatar_url)
        e.colour = member.colour
        await ctx.send(embed=e)

    @info.command(name='server', aliases=['guild'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Shows info about the current server."""

        guild = ctx.guild
        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        # we're going to duck type our way here
        class Secret:
            pass

        secret_member = Secret()
        secret_member.id = 0
        secret_member.roles = [guild.default_role]

        # figure out what channels are 'secret'
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            text_channels += is_text
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1

        regular_channels = len(guild.channels) - secret_channels
        voice_channels = len(guild.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in guild.members)

        e = discord.Embed()
        e.title = 'Info for ' + guild.name
        e.add_field(name='ID', value=guild.id)
        e.add_field(name='Owner', value=guild.owner)
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        if guild.splash:
            e.set_image(url=guild.splash_url)

        info = []
        info.append(tick(len(guild.features) >= 3, 'Partnered'))

        sfw = guild.explicit_content_filter is not discord.ContentFilter.disabled
        info.append(tick(sfw, 'Scanning Images'))
        info.append(tick(guild.member_count > 100, 'Large'))

        e.add_field(name='Info', value='\n'.join(map(str, info)))

        fmt = f'Text {text_channels} ({secret_channels} secret)\nVoice {voice_channels} ({secret_voice} locked)'
        e.add_field(name='Channels', value=fmt)

        fmt = f'Online: {member_by_status["online"]} ' \
              f'Idle: {member_by_status["idle"]} ' \
              f'DND: {member_by_status["dnd"]} ' \
              f'Offline: {member_by_status["offline"]}\n' \
              f'Total: {guild.member_count}'

        e.add_field(name='Members', value=fmt)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed()
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def permissions(self, ctx, *, member: discord.Member = None):
        """Shows a member's permissions.
        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = ctx.message.channel
        if member is None:
            member = ctx.message.author

        await self.say_permissions(ctx, member, channel)

    @commands.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    async def botpermissions(self, ctx):
        """Shows the bot's permissions.
        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.
        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = ctx.channel
        member = ctx.guild.me
        await self.say_permissions(ctx, member, channel)

    '''@commands.group(aliases=['leaderboards', 'lb'])
    @commands.guild_only()
    async def leaderboard(self, ctx):
        """Get different leaderboards."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")
    @leaderboard.command(aliases=['point'])
    async def points(self, ctx):
        """"Displays guild points leaderboards."""
        points = await db.get_all_points(ctx.guild.id)
        top_points = sorted(points, reverse=True)
        entries = []
        for p in top_points:
            try:
                user = self.bot.get_user(int(points[p]))
                entries.append("\t|\t__**"+user.name+"**__`#"+str(user.discriminator)+"`\n\n\t\t\t\t`POINTS:`  **"+str(p)+"**\n"+"\t"*16+";")
                if user.id == ctx.author.id:
                    title = "You rank: "+str(top_points.index(p)+1)+"/"+str(len(top_points))
            except:
                pass
        p = Pages(ctx, entries=entries, per_page=10)
        p.embed.title = title
        await p.paginate()'''

    '''@commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        """Manages the server's custom prefixes.
        If called without a subcommand, this will list the currently set
        prefixes.
        """

        prefixes = self.bot.get_guild_prefixes(ctx.guild)

        # we want to remove prefix #2, because it's the 2nd form of the mention
        # and to the end user, this would end up making them confused why the
        # mention is there twice
        del prefixes[1]

        e = discord.Embed(title='Prefixes', colour=discord.Colour.blurple())
        e.set_footer(text=f'{len(prefixes)} prefixes')
        e.description = '\n'.join(f'{index}. {elem}' for index, elem in enumerate(prefixes, 1))
        await ctx.send(embed=e)

    @prefix.command(name='add', ignore_extra=False)
    @checks.is_mod()
    async def prefix_add(self, ctx, prefix: Prefix):
        """Appends a prefix to the list of custom prefixes.
        Previously set prefixes are not overridden.
        To have a word prefix, you should quote it and end it with
        a space, e.g. "hello " to set the prefix to "hello ". This
        is because Discord removes spaces when sending messages so
        the spaces are not preserved.
        Multi-word prefixes must be quoted also.
        You must have Manage Server permission to use this command.
        """

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)
        current_prefixes.append(prefix)
        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(f'{tick(False)} {e}')
        else:
            await ctx.send(tick(True))

    @prefix_add.error
    async def prefix_add_error(self, ctx, error):
        if isinstance(error, commands.TooManyArguments):
            await ctx.send("You've given too many prefixes. Either quote it or only do it one by one.")

    @prefix.command(name='remove', aliases=['delete'], ignore_extra=False)
    @checks.is_mod()
    async def prefix_remove(self, ctx, prefix: Prefix):
        """Removes a prefix from the list of custom prefixes.
        This is the inverse of the 'prefix add' command. You can
        use this to remove prefixes from the default set as well.
        You must have Manage Server permission to use this command.
        """

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)

        try:
            current_prefixes.remove(prefix)
        except ValueError:
            return await ctx.send('I do not have this prefix registered.')

        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(f'{tick(False)} {e}')
        else:
            await ctx.send(tick(True))

    @prefix.command(name='clear')
    @checks.is_mod()
    async def prefix_clear(self, ctx):
        """Removes all custom prefixes.
        After this, the bot will listen to only mention prefixes.
        You must have Manage Server permission to use this command.
        """

        await self.bot.set_guild_prefixes(ctx.guild, [])
        await ctx.send(tick(True))'''

    @commands.command(aliases=["bl"])
    @commands.guild_only()
    async def bots(self, ctx):
        e = discord.Embed()
        e.title = "List of bots"
        e.colour = get_random_embed_color()
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        entries = []
        for m in ctx.guild.members:
            if m.bot:
                entries.append(m.display_name)
        p = Pages(ctx, entries=entries, per_page=10)
        await p.paginate()

def setup(bot):
    bot.add_cog(Guild(bot))
