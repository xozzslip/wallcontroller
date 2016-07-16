class CommunityDoesNotExist(Exception):
    """The community with that url does not exist"""
    pass


class VkApiError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return("CODE: {}, {}".format(self.code, self.message))
