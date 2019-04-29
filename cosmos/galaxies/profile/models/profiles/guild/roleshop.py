from .....guild._models.roleshop import Roles


class MemberRoleShop(object):

    def __init__(self, profile, **kwargs):
        self.profile = profile
        raw_roleshop = kwargs.get("roleshop", dict())
        self.roles = Roles()
        self.profile.plugin.bot.loop.create_task(
            self.__fetch_roles(raw_roleshop.get("roles", list())))

    async def __fetch_roles(self, raw_roles):
        roles = (await self.profile.fetch_guild_profile()).roleshop.roles
        self.roles = [role for role in roles if role.id in raw_roles]
