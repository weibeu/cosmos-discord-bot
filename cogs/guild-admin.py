from discord.ext import commands
from cogs.utils import db, util
from cogs.utils import checks
from cogs.utils.util import get_random_color, get_random_embed_color
from cogs.utils.rmenu import Menu, confirm_menu, FieldMenu
from cogs.utils.paginator import FieldPages
import re
import discord
import asyncio
import time
import argparse, shlex

class MEMBER(object):
    def __init__(self, name=None, joined_at=None, status=None, mention=None, display_name=None, avatar_url=None, discriminator=None, id=None):
        self.name = name
        self.joined_at = joined_at
        self.status = status
        self.mention = mention
        self.display_name = display_name
        self.avatar_url = avatar_url
        self.discriminator = discriminator
        self.id = id

def check_pm(ctx):
    return ctx.guild is None

class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)

class Guild_Admin(object):
    """Cog fot guild admins"""
    def __init__(self, bot):
        self.bot = bot
        self.r_s = {}
        self.omjcd_settings = {}
        self.sc_settings = {}
        self.guilds_rs_roles = {}
        self.welcome_settings = {}
        bot.loop.create_task(self.get_guild_settings())

    async def get_guild_settings(self):
        await self.bot.wait_until_ready()
        self.r_s = await db.get_reactor_settings(self.bot.guilds)
        self.omjcd_settings = await db.get_omjcd_settings(self.bot.guilds)
        self.sc_settings = await db.get_sc_settings(self.bot.guilds)
        self.guilds_rs_roles = await db.get_guilds_rs_roles(self.bot.guilds)
        self.welcome_settings = await db.get_welcome_settings(self.bot.guilds)

    """async def on_member_update(self, before, after):
        if before.roles != after.roles and list(set(after.roles)-set(before.roles))[0].id in self.guilds_rs_roles:
            """

    @commands.group(hidden=True, name="rsa")
    @commands.has_permissions(manage_roles=True)
    @commands.guild_only()
    async def role_shop_admin(self, ctx):
        """__**Role Shop Admin**__\n\nCommands to manange role shop"""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called")

    @role_shop_admin.command(name="create")
    async def create_role(self, ctx, role, points):
        """Creates a role for role shop worth provided number of points.
        Note: If your role name contains space or gap in between words, consider putting it into quotes.
        rn you can create maximum 50 roles.\nFor best appearence of role shop, consider keeping even number of roles in your role shop."""
        roles = await db.get_role_shop_dict(ctx)
        if len(roles) == 50:
            await ctx.send("Sorry, but rn you can't create more than 50 roles.")
            return
        else:
            if points.isnumeric():
                r = await ctx.guild.create_role(name=role, reason="Role Shop")
                await db.role_shop_create(ctx, r, points)
                td = self.guilds_rs_roles[str(ctx.guild.id)] #runtime dict
                td[str(r.id)] = str(points)
                self.guilds_rs_roles[str(ctx.guild.id)] = td
                await ctx.send("Role `"+role+"` created worth `"+points+"` points.")
            else:
                await ctx.send("Points should be numeric.")

    @role_shop_admin.command()
    async def roles(self, ctx):
        """View all created roles and required points to purchase."""
        roles = await db.get_role_shop_list(ctx)
        if roles == []:
            await ctx.send("No roles created yet for role shop.")
            return
        p = FieldPages(ctx, entries=roles, per_page=12, inline=True)
        p.embed.title = "Role Shop"
        p.embed.description = "```css\n List of purchasable roles created for role shop.```"
        await p.paginate()

    @role_shop_admin.command(name="remove")
    async def remove_role(self, ctx):
        """Deletes a role from role shop."""
        roles = await db.get_role_shop_dict(ctx)
        entries = []
        for r in roles:
            role = discord.utils.get(ctx.guild.roles, id=int(r))
            entries.append(("\t\t**"+role.name+"**", "`POINTS:` "+roles[r]))
        menu = FieldMenu(ctx, entries=entries, per_page=6, inline=True)
        menu.embed.title = "Remove Role Menu - Role Shop Admin"
        menu.embed.description = "```css\n React with corresponding emoji to remove that role.```"
        index = await menu.paginate()
        try:
            role_id = list(roles.keys())[index]
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
            if await confirm_menu(ctx, "Are you sure to delete __**"+role.name+"**__?"):
                await role.delete(reason="Delete role from Role-Shop")
                await db.remove_role(ctx.guild.id, role.id) #deleting role from role shop db
                await db.remove_deleted_purchased_role(ctx.guild.id, role.id) #deleting role from members document in db
                td = self.guilds_rs_roles[str(ctx.guild.id)] #runtime dict
                try:
                    td.pop(str(role.id))
                except:
                    pass
                self.guilds_rs_roles[str(ctx.guild.id)] = td
                await ctx.send("role, `"+role.name+"` removed.")
        except:
            pass

    @role_shop_admin.command(name="modify")
    async def modify_role(self, ctx):
        """Command to modify points of any role."""
        roles = await db.get_role_shop_dict(ctx)
        entries = []
        for r in roles:
            role = discord.utils.get(ctx.guild.roles, id=int(r))
            entries.append(("\t\t**"+role.name+"**", "`POINTS:` "+roles[r]))
        menu = FieldMenu(ctx, entries=entries, per_page=6, inline=True)
        menu.embed.title = "Role Modification Menu - Role Shop Admin"
        menu.embed.description = "```css\n React with corresponding emoji and send new points for the role to modify it.```"
        index = await menu.paginate()
        try:
            role_id = list(roles.keys())[index]
            modify_role = discord.utils.get(ctx.guild.roles, id=int(role_id))
        except:
            pass
        def check1(new_points):
            return new_points.author == ctx.author
        def check2(choice, user):
            return user == ctx.author
        m = await ctx.send("Reply with new points for role `"+modify_role.name+"`")
        try:
            new_points = await self.bot.wait_for('message', timeout=120.0, check=check1)
        except asyncio.TimeoutError:
            await ctx.send("Timeout")
        for choice in util.get_reaction_yes_no():
            await new_points.add_reaction(util.get_reaction_yes_no()[choice])
        try:
            choice, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check2)
        except asyncio.TimeoutError:
            await ctx.send("Reaction Timeout")
        if choice.emoji.name+":"+str(choice.emoji.id) == util.get_reaction_yes_no()["yes"]:
            await db.role_shop_create(ctx, modify_role, new_points.content)
            await m.delete()
            await new_points.delete()
            await ctx.send("Role `"+modify_role.name+"` points set to `"+new_points.content+"`.")
        elif choice.emoji.name+":"+str(choice.emoji.id) == util.get_reaction_yes_no()["no"]:
            await m.delete()
            await new_points.delete()
            await ctx.send("Cancelled!")
        else:
            await ctx.send("Something went wrong (reaction error `util.get_reaction_yes_no()`")

    @role_shop_admin.command()
    async def credit(self, ctx, user:discord.User, points):
        """Credits given points to any user."""
        await db.give_points(ctx.guild.id, user.id, int(points))
        await ctx.send("Credited `"+points+"` to **"+user.name+"**.")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx, *, msg: str = None):
        """Embed given text. Ex: Do [p]embed for more help

        Example: [p]embed title=test this | description=some words | color=3AB35E | field=name=test value=test

        You do NOT need to specify every property, only the ones you want.

        **All properties and the syntax:**
        - title=<words>
        - description=<words>
        - color=<hex_value>
        - image=<url_to_image> (must be https)
        - thumbnail=<url_to_image>
        - author=<words> **OR** author=name=<words> icon=<url_to_image>
        - footer=<words> **OR** footer=name=<words> icon=<url_to_image>
        - field=name=<words> value=<words> (you can add as many fields as you want)
        - ptext=<words>

        NOTE: After the command is sent, the bot will delete your message and replace it with the embed. Make sure you have it saved or else you'll have to type it all again if the embed isn't how you want it.

        PS: Hyperlink text like so:
        \[text](https://www.whateverlink.com)

        PPS: Force a field to go to the next line with the added parameter inline=False"""
        if msg:
            if checks.embed_perms(ctx.message):
                ptext = title = description = image = thumbnail = color = footer = author = None
                timestamp = discord.Embed.Empty
                embed_values = msg.split('|')
                for i in embed_values:
                    color = get_random_color()
                    if i.strip().lower().startswith('ptext='):
                        ptext = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('title='):
                        title = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('description='):
                        description = i.strip()[12:].strip()
                    elif i.strip().lower().startswith('desc='):
                        description = i.strip()[5:].strip()
                    elif i.strip().lower().startswith('image='):
                        image = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('thumbnail='):
                        thumbnail = i.strip()[10:].strip()
                    elif i.strip().lower().startswith('colour='):
                        color = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('color='):
                        color = i.strip()[6:].strip()
                    elif i.strip().lower().startswith('footer='):
                        footer = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('author='):
                        author = i.strip()[7:].strip()
                    elif i.strip().lower().startswith('timestamp'):
                        timestamp = ctx.message.created_at
                    else:
                        if description is None and not i.strip().lower().startswith('field='):
                            description = i.strip()

                if color:
                    if color.startswith('#'):
                        color = color[1:]
                    if not color.startswith('0x'):
                        color = '0x' + color

                if ptext is title is description is image is thumbnail is color is footer is author is None and 'field=' not in msg:
                    await ctx.message.delete()
                    return await ctx.send(content=None,
                                                       embed=discord.Embed(description=msg))

                if color:
                    em = discord.Embed(timestamp=timestamp, title=title, description=description, color=int(color, 16))
                else:
                    em = discord.Embed(timestamp=timestamp, title=title, description=description)
                for i in embed_values:
                    if i.strip().lower().startswith('field='):
                        field_inline = True
                        field = i.strip().lstrip('field=')
                        field_name, field_value = field.split('value=')
                        if 'inline=' in field_value:
                            field_value, field_inline = field_value.split('inline=')
                            if 'false' in field_inline.lower() or 'no' in field_inline.lower():
                                field_inline = False
                        field_name = field_name.strip().lstrip('name=')
                        em.add_field(name=field_name, value=field_value.strip(), inline=field_inline)
                if author:
                    if 'icon=' in author:
                        text, icon = author.split('icon=')
                        if 'url=' in icon:
                            em.set_author(name=text.strip()[5:], icon_url=icon.split('url=')[0].strip(), url=icon.split('url=')[1].strip())
                        else:
                            em.set_author(name=text.strip()[5:], icon_url=icon)
                    else:
                        if 'url=' in author:
                            em.set_author(name=author.split('url=')[0].strip()[5:], url=author.split('url=')[1].strip())
                        else:
                            em.set_author(name=author)

                if image:
                    em.set_image(url=image)
                if thumbnail:
                    em.set_thumbnail(url=thumbnail)
                if footer:
                    if 'icon=' in footer:
                        text, icon = footer.split('icon=')
                        em.set_footer(text=text.strip()[5:], icon_url=icon)
                    else:
                        em.set_footer(text=footer)
                await ctx.send(content=ptext, embed=em)
            else:
                await ctx.send(self.bot.bot_prefix + 'No embed permissions in this channel.')
        else:
            msg = '```How to use the >embed command:\nExample: >embed title=test this | description=some words | color=3AB35E | field=name=test value=test\n\nYou do NOT need to specify every property, only the ones you want.' \
                  '\nAll properties and the syntax (put your custom stuff in place of the <> stuff):\ntitle=<words>\ndescription=<words>\ncolor=<hex_value>\nimage=<url_to_image> (must be https)\nthumbnail=<url_to_image>\nauthor=<words> **OR** author=name=<words> icon=<url_to_image>\nfooter=<words> ' \
                  '**OR** footer=name=<words> icon=<url_to_image>\nfield=name=<words> value=<words> (you can add as many fields as you want)\nptext=<words>\n\nNOTE: After the command is sent, the bot will delete your message and replace it with ' \
                  'the embed. Make sure you have it saved or else you\'ll have to type it all again if the embed isn\'t how you want it.\nPS: Hyperlink text like so: [text](https://www.whateverlink.com)\nPPS: Force a field to go to the next line with the added parameter inline=False```'
            await ctx.send(self.bot.bot_prefix + msg)
        try:
            await ctx.message.delete()
        except:
            pass

    @commands.group(hidden=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def reactor(self, ctx):
        """Reacts to every message sent in channel where reactor is on with specified emojis. Suitable for channels like `server-suggestions`."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called")

    @reactor.command(name="setup")
    async def setup_reactor(self, ctx):
        """Setup reactor in current channel. (*Note: Bot should be in guild from which emojis for reactor is used.)"""
        def check_reaction(reaction, user):
            return user == ctx.author
        def check_message(message):
            return message.author == ctx.author
        emojis = []
        await ctx.message.delete()
        t1 = await ctx.send("How many emojis you want to use?")
        try:
            message = await self.bot.wait_for('message', check=check_message, timeout=120.0)
        except asyncio.TimeoutError:
            await ctx.send("Timeout")
        n = int(message.content)
        await t1.delete()
        await message.delete()
        m = await ctx.send("React with emojis you want reactor to use.")
        for i in range(n):
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check_reaction)
                if reaction.custom_emoji:
                    emojis.append(reaction.emoji.name+":"+str(reaction.emoji.id))
                else:
                    emojis.append(reaction.emoji)
            except asyncio.TimeoutError:
                await ctx.send("Reaction Timeout")
        await m.delete()
        re = await ctx.send("Recorded emojis (This is how bot will react to messages):")
        for i in emojis:
            await re.add_reaction(i)
        c = await ctx.send("Confirm?")
        for choice in util.get_reaction_yes_no():
            await c.add_reaction(util.get_reaction_yes_no()[choice])
        try:
            choice, user = await self.bot.wait_for('reaction_add', timeout=120.0, check=check_reaction)
        except asyncio.TimeoutError:
            await ctx.send("Reaction Timeout")
        if choice.emoji.name+":"+str(choice.emoji.id) == util.get_reaction_yes_no()["yes"]:
            await db.setup_reactor(ctx, emojis)#dump settings
            await db.toggle_reactor_on(ctx)
            t4 = await ctx.send("Reactor setup completed and reactor toggled to on.")
            td = {str(ctx.channel.id): {"is_on": True, "emojis": emojis}}
            self.r_s[str(ctx.guild.id)] = td #runtime dict
            await re.delete()
            await c.delete()
            await asyncio.sleep(2.7)
            await t4.delete()
        elif choice.emoji.name+":"+str(choice.emoji.id) == util.get_reaction_yes_no()["no"]:
            await ctx.send("Cancelled!")
        else:
            await ctx.send("Something went wrong (reaction error `util.get_reaction_yes_no()`")

    @reactor.command()
    async def on(self, ctx):
        """Command to turn on reactor in current channel."""
        await db.toggle_reactor_on(ctx)
        self.r_s[str(ctx.guild.id)][str(ctx.channel.id)]["is_on"] = True
        await ctx.message.delete()
        t = await ctx.send("Reactor on in current channel.")
        await asyncio.sleep(2.7)
        try:
            await ctx.message.delete()
            await t.delete()
        except:
            pass

    @reactor.command()
    async def off(self, ctx):
        """Command to turn off reactor in current channel."""
        await db.toggle_reactor_off(ctx)
        self.r_s[str(ctx.guild.id)][str(ctx.channel.id)]["is_on"] = False
        await ctx.message.delete()
        t = await ctx.send("Reactor off in current channel.")
        await asyncio.sleep(2.7)
        try:
            await ctx.message.delete()
            await t.delete()
        except:
            pass

    async def on_message(self, message):
        if message.guild is None:
            return
        if str(message.guild.id) in self.r_s and str(message.channel.id) in self.r_s[str(message.guild.id)] and self.r_s[str(message.guild.id)][str(message.channel.id)]["is_on"]:
            for emoji in self.r_s[str(message.guild.id)][str(message.channel.id)]["emojis"]:
                try:
                    await message.add_reaction(emoji)
                except:
                    pass

    async def on_guild_role_delete(self, role):
        if str(role.guild.id) in self.guilds_rs_roles and str(role.id) in self.guilds_rs_roles[str(role.guild.id)]:
            await db.remove_role(role.guild.id, role.id)
            #remove from purchased roles as well
            await db.remove_deleted_purchased_role(role.guild.id, role.id)


    '''@commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["shut-up", "shut up"])
    async def shutup(self, ctx, channel_id=None):
        """Command to mute bot in specified channel"""
        if channel_id is None:
            channel = ctx.channel
        else:
            channel = discord.utils.get(ctx.guild.channels, id=int(channel_id))
        await db.shutup_bot(ctx.guild.id, channel.id)
        await ctx.send("Cosmos muted in `"+channel.name+"`.")

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(aliases=["un-shutup", "speak"])
    async def unshutup(self, ctx, channel_id=None):
        """Command to enable bot messages in specified channel"""
        if channel_id is None:
            channel = ctx.channel
        else:
            channel = discord.utils.get(ctx.guild.channels, id=int(channel_id))
        await db.unshutup_bot(ctx.guild.id)
        await ctx.send("Cosmos unmuted in `"+channel.name+"`.")'''

    @commands.group(hidden=True, aliases=["omjcd", "cdomj"], name="on_member_join_cooldown")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def cooldown_on_member_join(self, ctx):
        """Enable cooldown for newly joined members and force them to read particular channels."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called")

    @cooldown_on_member_join.command(name="setup")
    async def setup_omjcd(self, ctx):
        """Setup on member join cooldown.\nSetup your cooldown time, channels in preferred order (which would be unlocked instantly without cd on member join).\nNote: It is implemented on `@everyone` role."""
        def check(new_points):
            return new_points.author == ctx.author
        message = await ctx.send("Send cooldown in minutes.")
        while True:
            try:
                cd = await self.bot.wait_for('message', timeout=120.0, check=check)
                try:
                    cooldown = float(cd.content)
                    await message.delete()
                    break
                except ValueError:
                    await ctx.send("Cooldown should be numeric.")
            except asyncio.TimeoutError:
                await message.delete()
                await cd.delete()
                await ctx.send("Timeout!")
        if await confirm_menu(ctx, cd, custom_message=True):
            message = await ctx.send("Reply channels with no cooldowns.")
            try:
                c = await self.bot.wait_for('message', timeout=120.0, check=check)
                channels = c.channel_mentions
                await message.delete()
            except asyncio.TimeoutError:
                await message.delete()
                await cd.delete()
                await ctx.send("Timeout!")
        if await confirm_menu(ctx, c, custom_message=True):
            message = await ctx.send("Send name for new role which will be given to newly joined members with cd.")
            try:
                rt = await self.bot.wait_for('message', timeout=120.0, check=check)
                r = rt.content
                await message.delete()
            except asyncio.TimeoutError:
                await message.delete()
                await ctx.send("Timeout!")
        if await confirm_menu(ctx, rt, custom_message=True):
            c = ''
            channel_ids = []
            for channel in channels:
                c += channel.mention+" "
            e = discord.Embed()
            e.title = "Recorded settings"
            e.add_field(name="Cooldown", value=str(cooldown)+" minutes")
            e.add_field(name="Non-cd channels: ", value=c)
            e.add_field(name="Name of role:", value=r)
            e.colour = get_random_embed_color()
            await ctx.send(embed=e)
            message = await ctx.send("Continue?")
            if await confirm_menu(ctx, message, custom_message=True):
                #main starts here, creates role, sets perms
                role = await ctx.guild.create_role(name=r, reason="Role created for new members with cooldown.")
                for channel in ctx.guild.channels:
                    if channel in channels:
                        await channel.set_permissions(role, send_messages=False, read_messages=True)
                    else:
                        if isinstance(channel, discord.channel.TextChannel):
                            await channel.set_permissions(role, send_messages=False, read_messages=False)
                        elif isinstance(channel, discord.channel.VoiceChannel):
                            await channel.set_permissions(role, connect=False, speak=False, use_voice_activation=False)
                await db.setup_omjcd(ctx.guild.id, role.id, cooldown) #dumping settings to db
                td = {"enabled": False, "role": role.id, "cooldown": str(cooldown)}
                self.omjcd_settings[str(ctx.guild.id)] = td #runtime dict
                await ctx.send("Setup completed!\nYou can turn on cooldown mode for new users by `omjcd enable` command.")

    @cooldown_on_member_join.command(name="enable")
    async def enable_omjcd(self, ctx):
        """Command to enable cooldown mode for newly joined members."""
        await db.enable_omjcd(ctx)
        self.omjcd_settings[str(ctx.guild.id)]["enabled"] = True
        await ctx.send("OMJCD enabled.")

    @cooldown_on_member_join.command(name="disable")
    async def disable_omjcd(self, ctx):
        """Command to disable cooldown mode for newly joined members."""
        await db.disable_omjcd(ctx)
        self.omjcd_settings[str(ctx.guild.id)]["enabled"] = False
        await ctx.send("OMJCD disabled.")

    '''@cooldown_on_member_join.command()
    async def settings(self, ctx):
        """Displays guild OMJCD setings"""
        settings = await db.get_omjcd_setting(ctx.guild.id)
        if settings == {}:
            return
        '''

    async def on_member_join(self, member):
        M = MEMBER(name=member.name, joined_at=member.joined_at, status=member.status, mention=member.mention, display_name=member.display_name, avatar_url=member.avatar_url, discriminator=member.discriminator, id=member.id)
        try:
            if str(member.guild.id) in self.welcome_settings and self.welcome_settings[str(member.guild.id)]['private']['enabled']:
                template = self.welcome_settings[str(member.guild.id)]['private']['message']
                message = template.format(**M.__dict__)
                await member.send(message)
        except:
            pass
        if str(member.guild.id) in list(self.omjcd_settings.keys()) and self.omjcd_settings[str(member.guild.id)]["enabled"]:   #member was part of guild with these settings and omjcd mode is enabled
                role = discord.utils.get(member.guild.roles, id=int(self.omjcd_settings[str(member.guild.id)]["role"]))
                await member.add_roles(role, reason="For cooldown on member join.")
                await asyncio.sleep(float(self.omjcd_settings[str(member.guild.id)]["cooldown"])*60)
                await member.remove_roles(role, reason="Removing cooldown role.")
                try:
                    if str(member.guild.id) in self.welcome_settings and self.welcome_settings[str(member.guild.id)]['channel']['enabled']:
                        template = self.welcome_settings[str(member.guild.id)]['channel']['message']
                        message = template.format(**M.__dict__)
                        channel = discord.utils.get(member.guild.channels, id=int(self.welcome_settings[str(member.guild.id)]['channel']['channel']))
                        await channel.send(message)
                except:
                    pass
        else:
            try:
                if str(member.guild.id) in self.welcome_settings and self.welcome_settings[str(member.guild.id)]['channel']['enabled']:
                    template = self.welcome_settings[str(member.guild.id)]['channel']['message']
                    message = template.format(**M.__dict__)
                    channel = discord.utils.get(member.guild.channels, id=int(self.welcome_settings[str(member.guild.id)]['channel']['channel']))
                    await channel.send(message)
            except:
                pass

    @commands.group(hidden=True, aliases=["secret-confessions", "sc"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def secret_confessions(self, ctx):
        """Add secret confessoisn to your guild."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called")

    @secret_confessions.command(name="setup")
    async def setup_sc(self, ctx):
        """Setup secret confessions on you guild."""
        message_channel = await ctx.guild.create_text_channel(name="Secret-Confessions", reason="Channel created for secret confession messages.")
        log_channel = await ctx.guild.create_text_channel(name="logs-secret-confessions", reason="Channel create for secret confessions logs.")
        await message_channel.set_permissions(ctx.guild.default_role, reason="Denied normal users from sending messages directly.", send_messages=False)
        await log_channel.set_permissions(ctx.guild.default_role, reason="Denied normal users from wathing secret confessions logs and send messages.", read_messages=False, send_messages=False)
        e = discord.Embed()
        e.title = "Channels:"
        e.add_field(name="Message channel", value=message_channel.mention)
        e.add_field(name="Log channel", value=log_channel.mention)
        e.colour = get_random_embed_color()
        await ctx.send(embed=e)
        await db.setup_sc(ctx.guild.id, message_channel.id, log_channel.id) #dumping settings to db
        td = {"enabled": True, "message_channel": str(message_channel.id), "log_channel": str(log_channel.id)}
        self.sc_settings[str(ctx.guild.id)] = td #runtime dict
        await ctx.send("Setup Successfull.")
        help_message = await message_channel.send("Send me `;confess "+str(ctx.guild.id)+" <your content>` as dm to add secret confession.")
        await help_message.pin()

    @secret_confessions.command(name="enable")
    async def enable_sc(self, ctx):
        """Enable secret confessions."""
        await db.enable_sc(ctx)
        self.sc_settings[str(ctx.guild.id)]["enabled"] = True
        await ctx.send("Secret confessions enabled.")

    @secret_confessions.command(name="disable")
    async def disable_sc(self, ctx):
        """Disable secret confessions."""
        await db.disable_sc(ctx)
        self.sc_settings[str(ctx.guild.id)]["enabled"] = False
        await ctx.send("Secret confessions disabled.")

    @commands.command()
    async def confess(self, ctx, guild_id, *, content):
        """Confess secretly in channel if secret-confessions are enabled in that guild."""
        guild = self.bot.get_guild(int(guild_id))
        if self.sc_settings[str(guild.id)]["enabled"]:
            color = get_random_embed_color()
            message = discord.Embed()
            message.description = content
            message.colour = color
            log = discord.Embed()
            log.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            log.description = content
            log.set_footer(text="ID: "+str(ctx.author.id))
            log.add_field(name="Author: ", value=ctx.author.mention)
            log.colour = color
            message_channel = guild.get_channel(int(self.sc_settings[str(guild.id)]["message_channel"]))
            log_channel = guild.get_channel(int(self.sc_settings[str(guild.id)]["log_channel"]))
            await message_channel.send(embed=message)
            await log_channel.send(embed=log)

            #process confession
        else:
            await ctx.send("Secret confession disabled in `"+guild.name+"`.")

    @commands.group(hidden=True, aliases=['purge'])
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def remove(self, ctx):
        """Removes messages that meet a criteria.
        In order to use this command, you must have Manage Messages permissions.
        Note that the bot needs Manage Messages as well. These commands cannot
        be used in a private message.
        When the command is done doing its work, you will get a message
        detailing which users got removed and how many messages got removed.
        """

        if ctx.invoked_subcommand is None:
            help_cmd = self.bot.get_command('help')
            await ctx.invoke(help_cmd, command='remove')

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Too many messages to search given ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('I do not have permissions to delete messages.')
        except discord.HTTPException as e:
            return await ctx.send(f'Error: {e} (try a smaller search?)')


        deleted = len(deleted)
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append('')

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Successfully removed {deleted} messages.', delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @remove.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @remove.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @remove.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @remove.command(name='all')
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @remove.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @remove.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send('The substring length must be at least 3 characters.')
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @remove.command(name='bot')
    async def _bot(self, ctx, prefix=None, search=100):
        """Removes a bot user's messages and messages with their optional prefix."""

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)

    @remove.command(name='emoji')
    async def _emoji(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r'<:(\w+):(\d+)>')
        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @remove.command(name='reactions')
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f'Too many messages to search for ({search}/2000)')

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f'Successfully removed {total_reactions} reactions.')

    @remove.command()
    async def custom(self, ctx, *, args: str):
        """A more advanced purge command.
        This command uses a powerful "command line" syntax.
        Most options support multiple values to indicate 'any' match.
        If the value has spaces it must be quoted.
        The messages are only deleted if all options are met unless
        the `--or` flag is passed, in which case only if any is met.
        The following options are valid.
        `--user`: A mention or name of the user to remove.
        `--contains`: A substring to search for in the message.
        `--starts`: A substring to search if the message starts with.
        `--ends`: A substring to search if the message ends with.
        `--search`: How many messages to search. Default 100. Max 2000.
        `--after`: Messages must come after this message ID.
        `--before`: Messages must come before this message ID.
        Flag options (no arguments):
        `--bot`: Check if it's a bot user.
        `--embeds`: Check if the message has embeds.
        `--files`: Check if the message has attachments.
        `--emoji`: Check if the message has custom emoji.
        `--reactions`: Check if the message has reactions
        `--or`: Use logical OR for all options.
        `--not`: Use logical NOT for all options.
        """
        parser = Arguments(add_help=False, allow_abbrev=False)
        parser.add_argument('--user', nargs='+')
        parser.add_argument('--contains', nargs='+')
        parser.add_argument('--starts', nargs='+')
        parser.add_argument('--ends', nargs='+')
        parser.add_argument('--or', action='store_true', dest='_or')
        parser.add_argument('--not', action='store_true', dest='_not')
        parser.add_argument('--emoji', action='store_true')
        parser.add_argument('--bot', action='store_const', const=lambda m: m.author.bot)
        parser.add_argument('--embeds', action='store_const', const=lambda m: len(m.embeds))
        parser.add_argument('--files', action='store_const', const=lambda m: len(m.attachments))
        parser.add_argument('--reactions', action='store_const', const=lambda m: len(m.reactions))
        parser.add_argument('--search', type=int, default=100)
        parser.add_argument('--after', type=int)
        parser.add_argument('--before', type=int)

        try:
            args = parser.parse_args(shlex.split(args))
        except Exception as e:
            await ctx.send(str(e))
            return

        predicates = []
        if args.bot:
            predicates.append(args.bot)

        if args.embeds:
            predicates.append(args.embeds)

        if args.files:
            predicates.append(args.files)

        if args.reactions:
            predicates.append(args.reactions)

        if args.emoji:
            custom_emoji = re.compile(r'<:(\w+):(\d+)>')
            predicates.append(lambda m: custom_emoji.search(m.content))

        if args.user:
            users = []
            converter = commands.MemberConverter()
            for u in args.user:
                try:
                    user = await converter.convert(ctx, u)
                    users.append(user)
                except Exception as e:
                    await ctx.send(str(e))
                    return

            predicates.append(lambda m: m.author in users)

        if args.contains:
            predicates.append(lambda m: any(sub in m.content for sub in args.contains))

        if args.starts:
            predicates.append(lambda m: any(m.content.startswith(s) for s in args.starts))

        if args.ends:
            predicates.append(lambda m: any(m.content.endswith(s) for s in args.ends))

        op = all if not args._or else any
        def predicate(m):
            r = op(p(m) for p in predicates)
            if args._not:
                return not r
            return r

        args.search = max(0, min(2000, args.search)) # clamp from 0-2000
        await self.do_removal(ctx, args.search, predicate, before=args.before, after=args.after)

    @commands.group(hidden=True)
    @checks.is_mod()
    async def announce(self, ctx, *, content):
        """Make cool embed announcements in guild.\nFormat: `;announce <content> | [title] | [image url]`\nTo skip say `title`: `;announce <content> | | [image url]`"""
        if ctx.invoked_subcommand is None:
            await ctx.message.delete()
            embed = discord.Embed()
            embed.colour = get_random_embed_color()
            description = content.split("|")[0]
            try:
                title = content.split("|")[1]
            except:
                title = None
            try:
                embed.set_image(url=content.split("|")[2])
            except:
                pass
            embed.description = description
            if await confirm_menu(ctx, "Ping `@everyone`?"):
                embed.description += "\n"+ctx.guild.default_role
            embed.title = title
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
            message = await ctx.send(embed=embed)
            start_time = time.time()
            while time.time() - start_time <= 270:
                embed.colour = get_random_embed_color()
                await message.edit(embed=embed)
                await asyncio.sleep(0.37)

        '''@announce.command(name="edit")
    async def edit_announcement(self, ctx, announcement_id, *, new_content):
        """Replaces content of old announcement with new."""
        old_announcement = await ctx.channel.get_message(int(announcement_id))
        embed = old_announcement.embeds[0]
        description = new_content.split("edit "+announcement_id)[-1]
        try:
            title = new_content.split("|")[1]
        except:
            title = None
        try:
            embed.set_image(url=new_content.split("|")[2])
        except:
            pass
        embed.description = description
        embed.title = title
        await old_announcement.edit(embed=embed)
        await ctx.message.delete()'''

    @commands.command(hidden=True, name="privatemessage", aliases=['pm'])
    @checks.is_mod()
    async def private_message(self, ctx, member:discord.Member, *, message):
        """Send private message to specified user."""
        embed = discord.Embed()
        embed.colour = get_random_embed_color()
        embed.description = message
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await member.send(embed=embed)

    @commands.group(name="welcome")
    @commands.has_permissions(administrator=True)
    async def welcome_message(self, ctx):
        """Create customised welcome message for newly joined members.
        Vars provided:
        `name` ~ name of member
        `joined_at` ~ datetime object of member join
        `status` ~ current discord status of member
        `mention` ~ string used to mention member
        `display_name` ~ display name of member
        `avatar_url` ~ direct avatar url of member
        `discriminator` ~ discriminator of member
        `id` ~ id of member
        Use `{var}` in your custom message. Here is an example illustrating custom var in a message:
        `Hi {name}! Welcome to Cosmos. {mention}`.
        `Note:` If On Member join cooldown is enabled on your server then, channel welcome messages are sent when cooldown on member join gets over."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")
            return

    @welcome_message.group(name="private_message", aliases=['pm'])
    async def welcome_private_message(self, ctx):
        """Manage private welcome messages settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")
            return

    @welcome_private_message.command(name="setup")
    async def setup_welcome_private_message(self, ctx):
        """Setup private welcome messages for new members."""
        def check_message(m):
            return ctx.author.id == m.author.id and ctx.channel.id == m.channel.id
        await ctx.send("Reply with your custom message.")
        try:
            message = await self.bot.wait_for('message', check=check_message, timeout=120)
        except asyncio.TimeoutError:
            return
        if await confirm_menu(ctx, message, custom_message=True):
            if str(ctx.guild.id) not in self.welcome_settings:
                self.welcome_settings[str(ctx.guild.id)] = {}
            td = {"message": message.content, "enabled": False}   # runtime dict
            self.welcome_settings[str(ctx.guild.id)]["private"] = td
            await db.set_welcome_private_message(ctx.guild.id, message.content)
            await ctx.send("Welcome message set to `"+message.content+"`.\nEnable it using `;welcome pm enable")

    @welcome_private_message.command(name="enable", aliases=["on"])
    async def enable_welcome_private_message(self, ctx):
        """Enable previously set private messages on member join."""
        self.welcome_settings[str(ctx.guild.id)]["private"]["enabled"] = True   # update runtime dict
        await db.enable_welcome_private_message(ctx.guild.id)
        await ctx.send("Private welcome messages enabled.")

    @welcome_private_message.command(name="disable", aliases=["off"])
    async def disable_welcome_private_message(self, ctx):
        self.welcome_settings[str(ctx.guild.id)]["private"]["enabled"] = False  # update runtime dict
        await db.disable_welcome_private_message(ctx.guild.id)
        await ctx.send("Private welcome messages disabled.")

    @welcome_message.group(name="channel")
    async def welcome_channel_message(self, ctx):
        """Manage channel welcome messages settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")
            return

    @welcome_channel_message.command(name="setup")
    async def setup_channel_welcome_message(self, ctx):
        """Setup custom welcome messages for new members which is sent in specified channel."""
        def check_message(m):
            return ctx.author.id == m.author.id and ctx.channel.id == m.channel.id
        await ctx.send("Reply with your custom message.")
        try:
            message = await self.bot.wait_for('message', check=check_message)
        except asyncio.TimeoutError:
            return
        if await confirm_menu(ctx, message, custom_message=True):
            await ctx.send("Reply channel for welcome messages.")
            try:
                m = await self.bot.wait_for('message', check=check_message)
                channel = m.channel_mentions[0]
            except asyncio.TimeoutError:
                return
            except IndexError:
                await ctx.send("No channel mentioned.\nStart setup again.")
                return
            if await confirm_menu(ctx, m, custom_message=True):
                e = discord.Embed(colour=get_random_embed_color(), title="Recorded settings")
                e.add_field(name="Message", value=message.content, inline=False)
                e.add_field(name="Channel", value=channel.mention, inline=False)
                e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=e)
                if await confirm_menu(ctx, "Confirm settings?"):
                    if str(ctx.guild.id) not in self.welcome_settings:
                        self.welcome_settings[str(ctx.guild.id)] = {}
                    td = {"message": message.content, "channel": str(channel.id), "enabled": False} # runtime dict
                    self.welcome_settings[str(ctx.guild.id)]["channel"] = td
                    await db.set_welcome_channel_message(ctx.guild.id, message.content, channel.id)
                    await ctx.send("Channel welcome message configured. Enable it using `;welcome channel enable`.")

    @welcome_channel_message.command(name="enable", aliases=["on"])
    async def enable_welcome_channel_message(self, ctx):
        """Enable previously set channel messages on member join."""
        self.welcome_settings[str(ctx.guild.id)]["channel"]["enabled"] = True  # update runtime dict
        await db.enable_welcome_channel_message(ctx.guild.id)
        await ctx.send("Channel welcome messages enabled.")

    @welcome_channel_message.command(name="disable", aliases=["off"])
    async def disable_welcome_channel_message(self, ctx):
        """Disable previously set channel messages on member join."""
        self.welcome_settings[str(ctx.guild.id)]["channel"]["enabled"] = False  # update runtime dict
        await db.disable_welcome_channel_message(ctx.guild.id)
        await ctx.send("Channel welcome messages disabled.")














def setup(bot):
    bot.add_cog(Guild_Admin(bot))
