from discord.ext import commands
from cogs.utils import db, util
from cogs.utils.paginator import FieldPages
from cogs.utils.rmenu import confirm_menu, FieldMenu
import discord
import asyncio
import time

class Role_Shop(object):
    """Cog for guild role shop"""
    def __init__(self, bot):
        self.bot = bot
        self.cd = {}

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        try:
            if int(time.time()) - self.cd[message.author.id] > 13:
                await db.give_points(message.guild.id, message.author.id, 1)
                self.cd[message.author.id] = int(time.time())
        except KeyError:
            self.cd[message.author.id] = int(time.time())

    @commands.command()
    @commands.guild_only()
    async def points(self, ctx, *, user:discord.User = None):
        """Sends guild points of user."""
        if user is None:
            user = ctx.author
            points = await db.get_points(ctx.guild.id, user.id)
            await ctx.send(user.name+", you've **"+points+"** guild points.")
        else:
            points = await db.get_points(ctx.guild.id, user.id)
            await ctx.send(user.name+" has **"+points+"** guild points.")

    @commands.group(name="roleshop", aliases=["role-shop", "rs", "shop"])
    @commands.guild_only()
    async def role_shop(self, ctx):
        """Displays role shop."""
        if ctx.invoked_subcommand is None:
            roles = await db.get_role_shop_list(ctx)
            if roles == []:
                await ctx.send("No roles created yet for role shop.")
                return
            p = FieldPages(ctx, entries=roles, per_page=12, inline=True)
            p.embed.title = "Role Shop"
            p.embed.description = "```css\n List of purchasable roles created for role shop which can be purchased by earned points.```"
            await p.paginate()

    @role_shop.command(aliases=["purchase"])
    async def buy(self, ctx):
        """Opens an interactive menu to purchase roles fom role shop."""
        user_points = await db.get_points(ctx.guild.id, ctx.author.id)
        roles = await db.get_role_shop_buy_dict(ctx)
        role_shop = await db.get_role_shop_dict(ctx)
        if roles == {}:
            await ctx.send("No roles created yet for role shop.")
            return
        menu = FieldMenu(ctx, entries=list(roles.values()), per_page=6, inline=True)
        menu.embed.title = "Buy Meny - Role Shop"
        menu.embed.description = "```css\n React with corresponding emoji to purchase that role with your earned points in guild.```"
        index = await menu.paginate()
        try:
            role_id = list(roles.keys())[index]
            role = discord.utils.get(ctx.guild.roles, id=int(role_id))
            if int(user_points) >= int(role_shop[str(role.id)]):
                if await confirm_menu(ctx, "Are you sure to purchase role __**"+role.name+"**__ for ** "+str(role_shop[str(role.id)])+" ** points?"):
                    await db.buy_role(ctx, role.id)
                    points_left = await db.get_points(ctx.guild.id, ctx.author.id)
                    c = await confirm_menu(ctx, "Role __**"+role.name+"**__ purchased. `Left` **"+points_left+"** points. \n\nDo you want to equip it right now?")
                    if c:
                        await ctx.author.add_roles(role, reason="Role purchased from role shop")
                        await db.equip_user_role(ctx, role.id)
                        await ctx.send("Role `"+role.name+"` equipped.")
                    elif not c:
                        await ctx.send("Role not equipped, you may equip it using rs equip.")
                    else:
                        ctx.send("Something went wrong.") #error code
            else:
                await ctx.send("Sorry, but rn you don't have enough points to purchase `"+role.name+"`.")
        except discord.Forbidden:
            await ctx.send("Missing Permissions. Maybe check roles hierarchy?")
        except:
            pass

    @role_shop.command()
    async def purchased(self, ctx):
        """Shows your purchased roles from role shop."""
        roles = await db.get_user_roles_purchased_list(ctx)
        if roles == []:
            await ctx.send("No roles purchased yet from role shop.")
            return
        roles_dict = await db.get_role_shop_dict(ctx)
        entries = []
        for role in roles_dict:
            if role in roles:
                r = discord.utils.get(ctx.guild.roles, id=int(role))
                entries.append(("\t\t**"+r.name+"**", "`POINTS:` "+roles_dict[role]))
        p = FieldPages(ctx, entries=entries, per_page=12, inline=True)
        p.embed.title = "Purchased Roles - Role Shop"
        p.embed.description = "```css\n Here is list of your purchased roles from your guild role shop.```"
        await p.paginate()

    @role_shop.command()
    async def equip(self, ctx):
        """Opens an interactive menu to equip purchased roles."""
        roles = await db.get_user_roles_unequipped_list(ctx)
        if roles == []:
            await ctx.send("No uequipped roles found.")
            return
        r_d = await db.get_role_shop_dict(ctx)
        entries = []
        for r in roles:
            role = discord.utils.get(ctx.guild.roles, id=int(r))
            entries.append(("\t\t**"+role.name+"**", "`POINTS:` "+r_d[r]))
        menu = FieldMenu(ctx, entries=entries, per_page=6, inline=True)
        menu.embed.title = "Roles Equip Menu - Role Shop"
        menu.embed.description = "```css\n React with corresponding emoji to equip that role.```"
        index = await menu.paginate()
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(roles[index]))
            if await confirm_menu(ctx, "Are you sure to equip `"+role.name+"`?"):
                await ctx.author.add_roles(role, reason="Role purchased from role shop")
                await db.equip_user_role(ctx, role.id)
                await ctx.send("Role, `"+role.name+"` equipped.")
        except discord.Forbidden:
            await ctx.send("Missing Permissions. Maybe check roles hierarchy?")
        except:
            pass

    @role_shop.command()
    async def unequip(self, ctx):
        """Opens an interactive menu to unequip equipped roles."""
        roles = await db.get_user_roles_equipped_list(ctx)
        if roles == []:
            await ctx.send("No equipped roles found.")
            return
        r_d = await db.get_role_shop_dict(ctx)
        entries = []
        for r in roles:
            role = discord.utils.get(ctx.guild.roles, id=int(r))
            entries.append(("\t\t**"+role.name+"**", "`POINTS:` "+r_d[r]))
        menu = FieldMenu(ctx, entries=entries, per_page=6, inline=True)
        menu.embed.title = "Roles Unequip Menu - Role Shop"
        menu.embed.description = "```css\n React with corresponding emoji to unequip that role. You can always re-equip them later.```"
        index = await menu.paginate()
        try:
            role = discord.utils.get(ctx.guild.roles, id=int(roles[index]))
            if await confirm_menu(ctx, "Are you sure to unequip `"+role.name+"`?"):
                await ctx.author.remove_roles(role, reason="Role Unequipped")
                await db.unequip_user_role(ctx, role.id)
                await ctx.send("Role, `"+role.name+"` unequipped.")
        except discord.Forbidden:
            await ctx.send("Missing Permissions. Maybe check roles hierarchy?")
        except:
            pass

def setup(bot):
    bot.add_cog(Role_Shop(bot))
