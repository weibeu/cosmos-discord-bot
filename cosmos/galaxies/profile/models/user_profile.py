import datetime

from .experience import UserExperience
from .currency import Boson


class CosmosUserProfile(UserExperience, Boson):

    @property
    def _plugin(self):
        return self.__plugin

    @property
    def xp_buffer_cooldown(self):
        return self._xp_buffer_cooldown

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    def __init__(self, plugin, **kwargs):
        self.__plugin = plugin
        self.id: int = kwargs["user_id"]
        self.reps: int = kwargs.get("reps", 0)
        self.rep_datetime = kwargs.get("rep_datetime")
        # self.badges = []
        self.description: str = kwargs.get("description", str())
        UserExperience.__init__(self, kwargs.get("xp", 0), kwargs.get("level", 0))
        Boson.__init__(self, kwargs.get("bosons", 0))
        self.rank: int = None
        self.spouse: CosmosUserProfile = None
        # self.inventory = []
        # self.on_time: int = None
        self._xp_buffer_cooldown = kwargs.get("xp_buffer_cooldown", self._plugin.data.xp.buffer_cooldown)
        self.user = self._plugin.bot.get_user(self.id)
        self.__collection = self._plugin.profile_cache.collection

    @property
    def can_rep(self):
        if not self.rep_datetime:    # Using rep for first time.
            return True
        delta = datetime.datetime.now() - self.rep_datetime
        return delta.seconds >= self._plugin.data.profile.rep_cooldown*60*60

    @property
    def rep_delta(self):
        future = self.rep_datetime + datetime.timedelta(hours=self._plugin.data.profile.rep_cooldown)
        # noinspection PyTypeChecker
        delta = future - datetime.datetime.now()
        hours, _ = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(_, 60)
        return hours, minutes, seconds

    async def rep(self, author_profile):
        self.reps += 1
        author_profile.rep_datetime = datetime.datetime.now()
        await self.__collection.update_one(
            {"user_id": self.id}, {"$set": {"reps": self.reps}}
        )
        await self.__collection.update_one(
            {"user_id": author_profile.id}, {"$set": {"rep_datetime": author_profile.rep_datetime}}
        )

    def to_update_document(self) -> tuple:
        filter_ = {"user_id": self.id}
        update = {
            "$set": {
                "xp": self.xp,
                "level": self.level
            }
        }
        return filter_, update

    def get_embed(self):
        embed = self._plugin.bot.theme.embeds.primary(title="Cosmos Profile")
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name="Level", value=str(self.level))
        embed.add_field(name="Experience points", value=str(self.xp))
        embed.add_field(name="Delta Experience points", value=str(self.delta_xp))
        embed.add_field(name="Reputation points", value=str(self.reps))
        embed.add_field(name="Bosons", value=str(self.bosons))
        description = self.description or self._plugin.data.profile.default_description
        embed.add_field(name="Profile description", value=description)
        return embed
