class ActionsBase(object):

    auto = False
    TITLE = str()

    def __init__(self, auto=False):
        self.auto = auto
        if self.auto:
            self.__class__.__name__ = f"[Auto] {self.__class__.__name__}"

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
