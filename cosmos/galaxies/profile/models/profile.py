from .level import UserLevel
from .experience import UserExperience
from .currency import CosmosCurrency


class CosmosUserProfile(UserLevel, UserExperience, CosmosCurrency):

    def __init__(self, bot, _id: int = None):
        self._bot = bot
        super().__init__()
        self.id: int = _id
        self.reps: int = None
        # self.badges = []
        self.description: str = None
        self.rank: int = None
        self.spouse: CosmosUserProfile = None
        # self.inventory = []
        # self.on_time: int = None

    @property
    def bot(self):
        return self._bot
