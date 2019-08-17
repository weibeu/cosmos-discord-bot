class ActionBaseMeta(type):

    auto = False
    TITLE = str()

    def __str__(self):
        if self.auto:
            return f"[Auto] {self.TITLE}"
        return self.TITLE


class ActionsBase(metaclass=ActionBaseMeta):

    TITLE = str()

    def __init__(self, auto=False):
        self.auto = auto

    @property
    def __name__(self):
        if self.auto:
            return f"[Auto] {self.__class__.__name__}"
        return self.__class__.__name__

    def __str__(self):
        if self.auto:
            return f"[Auto] {self.TITLE}"
        return self.TITLE


class Warned(ActionsBase):

    TITLE = "Member Warned"


class Kicked(ActionsBase):

    TITLE = "Member Kicked"


class Banned(ActionsBase):

    TITLE = "User Banned"


class Unbanned(ActionsBase):

    TITLE = "User Unbanned"


class Muted(ActionsBase):

    TITLE = "Member Muted"


class UnMuted(ActionsBase):

    TITLE = "Member Unmuted"
