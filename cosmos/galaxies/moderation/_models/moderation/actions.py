class ActionsBase(object):

    TITLE = str()

    def __str__(self):
        return self.TITLE


class Warned(ActionsBase):

    TITLE = "Member Warned"


class Kicked(ActionsBase):

    TITLE = "Member Kicked"


class Banned(ActionsBase):

    TITLE = "User Banned"
