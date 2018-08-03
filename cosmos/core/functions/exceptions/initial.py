class FatalError(Exception):

    def __init__(self, message=None):
        self._message = "A fatal error has occurred. Unable to continue without resolving."
        self.message = message

    def __str__(self):
        print(self._message)
        if self.message is not None:
            print(self.message)
