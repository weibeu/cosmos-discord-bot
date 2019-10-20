from .. import Cog, UserNotPrime
from discord.ext import commands


class Tags(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    async def __tags_parser(self, _, tag, __):
        if len(tag.content) > self.plugin.data.tags.tags_excerpt_size:
            return tag.name, tag.content[:self.plugin.data.tags.tags_excerpt_size] + " ..."
        return tag.name, tag.content

    @Cog.command(name="tags")
    async def tags(self, ctx):
        profile = await ctx.fetch_cosmos_user_profile()
        if not profile.tags:
            return await ctx.send_line(f"❌    You haven't created any custom tags yet.")
        paginator = ctx.get_field_paginator(profile.tags, entry_parser=self.__tags_parser, inline=False)
        paginator.embed.title = "Custom Tags"
        await paginator.paginate()

    @Cog.group(name="tag", invoke_without_command=True)
    async def tag(self, ctx, *, name):
        profile = await ctx.fetch_cosmos_user_profile()
        if not profile.tags:
            return await ctx.send_line(f"❌    You haven't created any custom tags yet.")
        tag = profile.get_tag(name)
        if not tag:
            return await ctx.send_line(f"❌    Can't find any tag with provided name.")
        embed = ctx.embeds.one_line.primary(name, ctx.author.avatar_url)
        content = tag.content
        # Check if tag content contains any images and consider very first image url.
        try:
            url = self.bot.utilities.find_image_urls(tag.content)[0]
        except IndexError:
            pass
        else:
            embed.set_image(url)
            content = content.replace(url, str())
        embed.description = content
        await ctx.send(embed=embed)

    @tag.command(name="create")
    async def create_tag(
            self, ctx, name, *, content: commands.clean_content(use_nicknames=False, fix_channel_mentions=True)):
        profile = await ctx.fetch_cosmos_user_profile()
        if len(profile.tags) >= self.plugin.data.tags.max_tags and not profile.is_prime:
            raise UserNotPrime
        if profile.get_tag(name):
            if not await ctx.confirm(f"⚠    You already have existing tag with same name. Replace with new content?"):
                return
        await profile.create_tag(name, content)
        await ctx.send_line(f"✅    Tag {name} has been created.")

    @tag.command(name="remove", aliases=["delete"])
    async def remove_tag(self, ctx, *, name):
        profile = await ctx.fetch_cosmos_user_profile()
        if not profile.get_tag(name):
            return await ctx.send_line(f"❌    You don't own any tag with such name.")
        if not await ctx.confirm(f"⚠   Are you sure to remove tag {name}?"):
            return
        await profile.remove_tag(name)
        await ctx.send_line(f"✅    Tag {name} has been removed.")
