"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import discord

from .. import Cog


class Profile(Cog):
    """Plugin which implements Cosmos Profile."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = self.plugin.cache
        if self.plugin.data.profile.__dict__.get("cache_all"):
            self.bot.loop.create_task(self.cache.prepare())

    @Cog.listener()
    async def on_patreon_members_pledge_create(self, user):
        profile = await user.fetch_cosmos_user_profile()
        await profile.make_prime(tier=user.tier)
        if not user.is_former:
            try:
                fermions = self.plugin.data.fermions.prime_benifits[user.tier.name]
            except KeyError:
                pass
            else:
                await profile.give_fermions(fermions)

    @Cog.listener()
    async def on_patreon_members_pledge_delete(self, user):
        profile = await user.fetch_cosmos_user_profile()
        await profile.remove_prime()

    @Cog.listener()
    async def on_patreon_members_pledge_update(self, user):
        profile = await user.fetch_cosmos_user_profile()
        await profile.make_prime(tier=user.tier)

    @Cog.group(invoke_without_command=True)
    async def profile(self, ctx, *, user: discord.Member = None):
        """Displays your Cosmos Profile or of specified member."""
        user = user or ctx.author
        profile = await self.cache.get_profile(user.id)
        if profile is None:
            res = self.plugin.data.responses.no_profile.format(user_name=user.name)
            return await ctx.send_line(res)
        await ctx.send(embed=await profile.get_embed())

    @profile.group(name="description", aliases=["text"], invoke_without_command=True)
    async def profile_description(self, ctx):
        """Displays currently set profile description."""
        profile = await self.cache.get_profile(ctx.author.id)
        embed = self.bot.theme.embeds.primary()
        embed.set_author(name=f"{ctx.author.name}'s Profile Description", icon_url=ctx.author.avatar_url)
        embed.description = profile.description
        await ctx.send(embed=embed)

    @profile_description.command(name="set", aliases=["modify", "edit", "change"])
    async def set_profile_description(self, ctx, *, description: str):
        """Add description to your profile. The profile description can't exceed char length of 250."""
        max_words = self.plugin.data.profile.max_description_length
        if len(description) > max_words:
            res = f"❌    Sorry but profile description cannot exceed {max_words} word limit."
            return await ctx.send_line(res)
        profile = await self.cache.get_profile(ctx.author.id)
        await profile.set_description(description)
        embed = self.bot.theme.embeds.primary(title="✅    Your Profile Description has been updated to:")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.description = profile.description
        await ctx.send("", embed=embed)

    @profile.group(name="birthday", aliases=["birthdate", "bday"], invoke_without_command=True)
    async def profile_birthday(self, ctx):
        """Displays your birthday if it has been set already."""
        profile = await self.cache.get_profile(ctx.author.id)
        if not profile.birthday:
            res = "You have not set your birthday on your profile yet."
            return await ctx.send_line(res, ctx.author.avatar_url)
        res = f"Your birthday is on {profile.birthday.strftime('%e %B')}."
        await ctx.send_line(res, ctx.author.avatar_url)

    @profile_birthday.command(name="set")
    async def set_profile_birthday(self, ctx, *, birthday: str):
        """Set your birthday to show up on the Cosmos Profile. [DD-MM-YYYY]."""
        profile = await self.cache.get_profile(ctx.author.id)
        await profile.set_birthday(birthday)
        res = f"Your birthday is set to {profile.birthday.strftime('%B %e, %Y | %A')}."
        await ctx.send_line(res, ctx.author.avatar_url)

    @Cog.command(name="rep")
    async def rep_user(self, ctx, *, user: discord.Member = None):
        """Add a reputation point to specified member."""
        if user and user.bot:
            return await ctx.send_line("😔    Sorry but I just can't do that.")
        if user and user.id == ctx.author.id:
            return await ctx.send_line("🙂    Nice try but wouldn't that be unfair?")
        author_profile = await self.cache.get_profile(ctx.author.id)
        if user is None:
            if author_profile.can_rep:
                res = "👌    You can rep someone now."
            else:
                res = f"⏳    You can rep again {author_profile.next_rep.humanize()}."
            return await ctx.send_line(res)

        if author_profile.can_rep:
            target_profile = await self.cache.get_profile(user.id)
            if not target_profile:
                res = self.plugin.data.responses.no_profile.format(user_name=user.name)
                return await ctx.send_line(res)
            await target_profile.rep(author_profile)
            res = f"You added one reputation point to {user.name}."
            await ctx.send_line(res, ctx.author.avatar_url)
        else:
            res = f"⏳    You can rep again {author_profile.next_rep.humanize()}."
            await ctx.send_line(res)
