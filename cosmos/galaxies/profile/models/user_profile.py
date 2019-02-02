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
        UserLevel.__init__(self)
        self.rank: int = None
        self.spouse: CosmosUserProfile = None
        # self.inventory = []
        # self.on_time: int = None

    @classmethod
    def from_document(cls, document: dict):
        return cls(**document)
