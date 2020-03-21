from .core import Cosmos
from .core.functions import exceptions


__release__ = "alpha"
__version__ = "0.0.1"


def get_bot():
    return Cosmos(version=__version__, release=__release__)
