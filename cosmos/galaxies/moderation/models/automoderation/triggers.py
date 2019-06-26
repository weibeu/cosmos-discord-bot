from .actions import AutoModerationActions


__triggers__ = [
    "banned_words",
]


class AutoModerationTrigger(object):

    def __init__(self, **_document):
        self._document = _document
        self.name = self._document["name"]
        self._actions = self._document["actions"]

    @property
    def actions(self):
        return [getattr(AutoModerationActions, _) for _ in self._actions]

    def __getattr__(self, item):
        try:
            return self._document[item]
        except KeyError:
            raise AttributeError

    @property
    def title(self):
        return self.name.replace("_", " ").title()

    async def dispatch(self, member):
        for action in self.actions:
            await action(member)

    @property
    def document(self):
        return {
            "name": self.name,
            "actions": [_.__name__ for _ in self.actions],
        }


_base = AutoModerationTrigger
