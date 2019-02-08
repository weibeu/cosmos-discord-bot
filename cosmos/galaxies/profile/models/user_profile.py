import datetime

from .currency import Boson
from .experience import UserExperience
from .marriage import CosmosMarriage


class CosmosUserProfile(UserExperience, Boson, CosmosMarriage):

    @property
    def _plugin(self):
        return self.__plugin

    @property
    def _collection(self):
        return self.__collection

    @property
    def id(self):
        return self._id

    @property
    def description(self):
        return self._description or self._plugin.data.profile.default_description

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    def __init__(self, plugin, **kwargs):
        UserExperience.__init__(self, **kwargs)
        Boson.__init__(self, **kwargs)
        CosmosMarriage.__init__(self, **kwargs)
        self.__plugin = plugin
        self._id: int = kwargs["user_id"]
        raw_reputation = kwargs.get("reputation", dict())
        self.reps: int = raw_reputation.get("points", 0)
        self.rep_datetime = raw_reputation.get("datetime")
        # self.badges = []
        self._description: str = kwargs.get("description", str())
        self.rank: int = None
        # self.inventory = []
        # self.on_time: int = None
        self.user = self._plugin.bot.get_user(self.id)
        self.__collection = self._plugin.profile_cache.collection

    @property
    def can_rep(self):
        if not self.rep_datetime:    # Using rep for first time.
            return True
        delta = datetime.datetime.now() - self.rep_datetime
        return delta.seconds >= self._plugin.data.profile.rep_cooldown*60*60

    @property
    def rep_delta(self) -> tuple:
        return self.time_delta(self.rep_datetime, self._plugin.data.profile.rep_cooldown)

    async def rep(self, author_profile):
        self.reps += 1
        author_profile.rep_datetime = datetime.datetime.now()
        await self._collection.update_one(
            {"user_id": self.id}, {"$set": {"reputation.points": self.reps}}
        )
        await self._collection.update_one(
            {"user_id": author_profile.id}, {"$set": {"reputation.datetime": author_profile.rep_datetime}}
        )

    async def set_description(self, description: str):
        self._description = description
        await self._collection.update_one(
            {"user_id": self.id}, {"$set": {"description": self.description}}
        )

    def to_update_document(self) -> tuple:
        filter_ = {"user_id": self.id}
        update = {
            "$set": {
                "xp": self.xp,
                "level": self.level,
                "currency.bosons": self.bosons
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
        embed.add_field(name="Profile description", value=self.description)
        return embed
