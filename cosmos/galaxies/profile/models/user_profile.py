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

    def to_xp_filter_and_update(self) -> tuple:
        filter_ = {"user_id": self.id}
        update = {
            "$set": {
                "xp": self.xp,
                "level": self.level
            }
        }
        return filter_, update
