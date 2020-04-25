from .. import Cog, UserNotPrime
from discord.ext import commands


class Tags(Cog):
    """Tags to hold and save texts or images which can be retrieved anytime later across different servers."""

    INESCAPABLE = False

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def __tags_parser(self, _, tag, __):
        if len(tag.content) > self.plugin.data.tags.tags_excerpt_size:
            return tag.name, tag.content[:self.plugin.data.tags.tags_excerpt_size] + " ..."
        return tag.name, tag.content

    @Cog.command(name="tags")
    async def tags(self, ctx):
        """Displays list of custom tags created and owned by you."""
        profile = await ctx.fetch_cosmos_user_profile()
        if not profile.tags:
            return await ctx.send_line(f"❌    You haven't created any custom tags yet.")
        paginator = ctx.get_field_paginator(profile.tags, entry_parser=self.__tags_parser, inline=False)
        paginator.embed.set_author(name=f"{ctx.author.display_name}'s Custom Tags", icon_url=ctx.author.avatar_url)
        paginator.embed.description = "```css\nDisplaying custom tags created by you.```"
        await paginator.paginate()

    @Cog.cooldown(1, 3, Cog.bucket_type.user)
    @Cog.group(name="tag", invoke_without_command=True)
    async def tag(self, ctx, *, name):
        """Retrieves and displays specified tag and all of its contents."""
        profile = await ctx.fetch_cosmos_user_profile()
        if not profile.tags:
            return await ctx.send_line(f"❌    You haven't created any custom tags yet.")
        tag = profile.get_tag(name)
        if not tag:
            return await ctx.send_line(f"❌    Can't find any tag with provided name.")
        embed = ctx.embeds.one_line.primary(name, self.bot.theme.images.file)
        content = tag.content
        # Check if tag content contains any images and consider very first image url.
        try:
            url = self.bot.utilities.find_image_urls(tag.content)[0]
        except IndexError:
            pass
        else:
            embed.set_image(url=url)
            content = content.replace(url, str())
        embed.description = content
        embed.set_footer(text=f"Tag | {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @tag.command(name="create")
    async def create_tag(
            self, ctx, name, *, content: commands.clean_content(use_nicknames=False, fix_channel_mentions=True) = ""):
        """Creates a new tag with specified name holding provided content."""
        if not (content or ctx.message.attachments):
            raise commands.UserInputError
        profile = await ctx.fetch_cosmos_user_profile()
        if len(profile.tags) >= self.plugin.data.tags.max_tags and not profile.is_prime:
            raise UserNotPrime
        if profile.get_tag(name):
            if not await ctx.confirm(f"⚠    You already have existing tag with same name. Replace with new content?"):
                return
        if ctx.message.attachments:
            content += f" {ctx.message.attachments[0].url}"
        await profile.create_tag(name, content)
        await ctx.send_line(f"✅    Tag {name} has been created.")

    @tag.command(name="remove", aliases=["delete"])
    async def remove_tag(self, ctx, *, name=None):
        """Permanently removes the specified tag."""
        profile = await ctx.fetch_cosmos_user_profile()
        if not name:
            menu = ctx.get_field_menu(profile.tags, self.__tags_parser, inline=False)
            menu.embed.title = "Remove Custom Tag"
            response = await menu.wait_for_response()
            name = response.entry.name
        if not profile.get_tag(name):
            return await ctx.send_line(f"❌    You don't own any tag with such name.")
        if not await ctx.confirm(f"⚠   Are you sure to remove tag {name}?"):
            return
        await profile.remove_tag(name)
        await ctx.send_line(f"✅    Tag {name} has been removed.")
