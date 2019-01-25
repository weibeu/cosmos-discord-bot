import discord
from discord.ext import commands

from cogs.utils import db
from cogs.utils.util import get_random_embed_color


class Logs(object):

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.bot.loop.create_task(self.get_settings())

    async def get_settings(self):
        await self.bot.wait_until_ready()
        self.cache = await db.get_log_settings(self.bot.guilds)
        for g in self.bot.guilds:
            await self.refresh_invites(g)

    async def refresh_invites(self, guild):
        try:
            c = self.cache[guild.id]
            invites = await guild.invites()
            c.update({"invites": invites})
            self.cache.update({guild.id: c})
        except:
            pass

    async def on_member_join(self, member):
        if member.guild.id in self.cache and self.cache[member.guild.id]["enabled"]:
            invite = None
            invites = await member.guild.invites()
            for i in invites:
                for old_invite in self.cache[member.guild.id]["invites"]:
                    if i.uses > old_invite.uses and i.id == old_invite.id:
                        invite = i
            if not invite:
                async for entry in member.guild.audit_logs():
                    if entry.action == discord.AuditLogAction.invite_create:
                        invite = entry.target
                        break

            await self.refresh_invites(member.guild)

            embed = discord.Embed(title="Member Joined", color=get_random_embed_color(), timestamp=member.joined_at)
            embed.add_field(name="Member", value=f"{member.mention} | {member}\n**ID:** `{member.id}`")
            embed.add_field(name="Joined at", value=f"{member.joined_at.strftime('%d - %B - %Y | %H : %M (GMT)')}")
            embed.add_field(name="Created at", value=f"{member.created_at.strftime('%d - %B - %Y')}")
            if invite is not None:
                if invite.created_at is not None:
                    embed.add_field(name="Invite",
                                    value=f"**URL:** {invite.url}\n**Inviter:** {invite.inviter.mention} | {invite.inviter}\n**Uses:** {invite.uses}\n**Created:** {invite.created_at.strftime('%d - %B - %Y | %H : %M (GMT)')}", inline=False)
                else:
                    embed.add_field(name="Invite",
                                    value=f"**URL:** {invite.url}\n**Inviter:** {invite.inviter.mention} | {invite.inviter}\n**Uses:** {invite.uses}",
                                    inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            log_channel = member.guild.get_channel(self.cache[member.guild.id].get("channel"))
            await log_channel.send(embed=embed)

    async def on_member_remove(self, member):
        if member.guild.id in self.cache and self.cache[member.guild.id]["enabled"]:
            embed = discord.Embed(title="Member Left", color=int("0xF44336", 16))
            embed.add_field(name="Member", value=f"{member} | {member}\n**ID:** `{member.id}`")
            embed.add_field(name="Joined at", value=f"{member.joined_at.strftime('%d - %B - %Y | %H : %M (GMT)')}")
            embed.add_field(name="Created at", value=f"{member.created_at.strftime('%d - %B - %Y')}")
            embed.set_thumbnail(url=member.avatar_url)
            log_channel = member.guild.get_channel(self.cache[member.guild.id].get("channel"))
            await log_channel.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.group(name="log")
    async def logger(self, ctx):
        if ctx.invoked_subcommand is None:
            pass

    @logger.command(name="setup")
    async def set_logger_channel(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        await db.set_log_channel(ctx.guild.id, channel.id)
        # update runtime dict
        c = {
            "channel": channel.id,
            "enabled": True
        }
        self.cache.update({ctx.guild.id: c})
        await ctx.send(f"Logs created and enabled for {channel.mention}.")

    @logger.command(name="enable")
    async def enable_logger(self, ctx):
        c: dict = self.cache[ctx.guild.id]
        c.update({"enabled": True})
        self.cache.update({ctx.guild.id: c})
        await db.enable_log_channel(ctx.guild.id)
        await ctx.message.add_reaction('✅')

    @logger.command(name="disable")
    async def disable_logger(self, ctx):
        c: dict = self.cache[ctx.guild.id]
        c.update({"enabled": False})
        self.cache.update({ctx.guild.id: c})
        await db.enable_log_channel(ctx.guild.id)
        await ctx.message.add_reaction('✅')

def setup(bot):
    bot.add_cog(Logs(bot))
