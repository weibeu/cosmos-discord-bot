from .level import UserLevel
from .experience import UserExperience
from .currency import CosmosCurrency


class CosmosUserProfile(UserExperience, UserLevel, CosmosCurrency):

    def __init__(self, **kwargs):
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

    @classmethod
    def from_document(cls, document: dict):
        return cls(**document)

    def to_document(self) -> dict:
        document = {
            "user_id": self.id,
            "reps": self.reps,
            "description": self.description,
            "level": self.level,
            "xp": self.xp
        }
        return document

    def to_xp_filter_and_update(self) -> tuple:
        filter_ = {"user_id": self.id}
        update = {
            "xp": self.xp,
            "level": self.level
        }
        return filter_, update
