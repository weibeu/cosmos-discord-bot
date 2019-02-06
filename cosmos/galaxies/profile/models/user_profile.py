from datetime import datetime

from .level import UserLevel
from .experience import UserExperience
from .currency import CosmosCurrency


class CosmosUserProfile(UserExperience, UserLevel, CosmosCurrency):

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
        UserExperience.__init__(self, kwargs.get("xp", 0))
        UserLevel.__init__(self, kwargs.get("level", 0))
        # CosmosCurrency.__init__(self, kwargs.get("currency_name", 0))
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
        return (self.rep_delta.seconds/60)/60 >= self._plugin.data.profile.rep_cooldown

    @property
    def rep_delta(self):
        return datetime.now() - self.rep_datetime

    async def rep(self):
        self.reps += 1
        self.rep_datetime = datetime.now()
        await self.__collection.update_one({"user_id": self.id}, {"$set": {"rep_datetime": datetime.now()}})

    def to_update_document(self) -> tuple:
        filter_ = {"user_id": self.id}
        update = {
            "$set": {
                "reps": self.reps,
                "xp": self.xp,
                "level": self.level
            }
        }
        return filter_, update

    def get_embed(self):
        embed = self._plugin.bot.theme.embeds.primary(title="Cosmos Profile")
        embed.set_author(name=self.user.name, icon_url=self.user.avatar_url)
        embed.add_field(name="Reputation points", value=str(self.reps))
        embed.add_field(name="Level", value=str(self.level))
        embed.add_field(name="Experience points", value=str(self.xp))
        embed.add_field(name="Experience points required for next level", value=str(self.delta_xp))
        description = self.description or self._plugin.data.profile.default_description
        embed.add_field(name="Profile description", value=description)
        return embed
