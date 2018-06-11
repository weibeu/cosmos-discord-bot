import discord
from discord.ext import commands
from cogs.utils import db
from cogs.utils.paginator import Pages
from cogs.utils.rmenu import Menu, confirm_menu
from cogs.utils import checks

class Tags(object):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tags(self, ctx):
        """View list of your all created tags."""
        tags = await db.get_tags(ctx.guild.id, ctx.author.id)
        if tags is None:
            await ctx.send("You don't have any created tags.")
            return
        p = Pages(ctx, entries=list(tags.keys()), per_page=10)
        await p.paginate()

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def tag(self, ctx, *, name):
        """Tag any text to retrieve it later.\nIf sub command is not called, then this will search for provided tag."""
        tag = await db.get_tag(ctx.guild.id, ctx.author.id, name)
        if tag is None:
            await ctx.send("Tag not found.")
            return
        await ctx.send(tag)

    @tag.command(name="create", aliases=["add", "new"])
    async def create_tag(self, ctx, name, *, content):
        """Create a new guild specific tag owned by you."""
        await db.create_tag(ctx.guild.id, ctx.author.id, name, content)
        await ctx.send("Tag `"+name+"` created.\nRetrieve it using `;tag "+name+"`.")
        await ctx.message.delete()

    @tag.command(name="remove", aliases=["delete", "drop"])
    async def remove_tag(self, ctx, name=None):
        """Remove created tag."""
        tags = await db.get_tags(ctx.guild.id, ctx.author.id)
        if tags is None:
            await ctx.send("You don't have any created tags.")
            return
        if name is None:
            menu = Menu(ctx, entries=list(tags.keys()), per_page=10)
            index = await menu.paginate()
            try:
                name = list(tags.keys())[index]
            except:
                pass
        if await confirm_menu(ctx, "Are you sure to remove tag __**"+name+"**__?"):
            await db.remove_tag(ctx.guild.id, ctx.author.id, name)
            await ctx.send("Tag `"+name+"` removed.")

    @commands.group(name="TagBox", aliases=["tb"])
    @commands.guild_only()
    async def tag_box(self, ctx):
        """Displays Tag Box\nTag Box is owned by guild, can be used by anyone in the guild."""
        if ctx.invoked_subcommand is None:
            tags = await db.get_tags_box(ctx.guild.id)
            if tags is None:
                await ctx.send("No tags in guild Tag Box.")
                return
            p = Pages(ctx, entries=list(tags.keys()), per_page=10)
            await p.paginate()

    @tag_box.command(name="tag")
    async def tag_box_tag(self, ctx, *, name):
        """Retrieve a tag from tag box."""
        tag = await db.get_tag_box(ctx.guild.id, name)
        if tag is None:
            await ctx.send("Tag not found.")
            return
        await ctx.send(tag)

    @tag_box.command(name="create", aliases=["add, new"])
    @checks.is_mod()
    async def create_tag_box(self, ctx, name, *, content: commands.clean_content):
        """Create a tag for Tag Box owned by guild.\ncan be only used by mods."""
        await db.create_tag_box(ctx.guild.id, name, content)
        await ctx.send("Tag `"+name+"` created.\nRetrieve it using `;tb tag "+name+"`.")
        await ctx.message.delete()

    @tag_box.command(name="remove", aliases=["delete", "drop"])
    @checks.is_mod()
    async def remove_tag_box(self, ctx, name=None):
        """Remove tag from Tag Box.\ncan be only used by mods."""
        tags = await db.get_tags_box(ctx.guild.id)
        if tags is None:
            await ctx.send("No tags in guild Tag Box.")
            return
        if name is None:
            menu = Menu(ctx, entries=list(tags.keys()), per_page=10)
            index = await menu.paginate()
            try:
                name = list(tags.keys())[index]
            except:
                pass
        if await confirm_menu(ctx, "Are you sure to remove tag __**"+name+"**__?"):
            await db.remove_tag_box(ctx.guild.id, name)
            await ctx.send("Tag `"+name+"` removed.")

def setup(bot):
    bot.add_cog(Tags(bot))
