class ActionsBaseMeta(type):

    def __new__(cls, *args, **kwargs):
        cls.auto = False
        cls.TITLE = str()
        return super().__new__(cls, *args, **kwargs)


class ActionsBase(metaclass=ActionsBaseMeta):

    def __init__(self, auto=False):
        self.auto = auto

    def __str__(self):
        if self.auto:
            return f"[Auto Mod] {self.TITLE}"
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
