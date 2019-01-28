class DcimBase(object):
    # All dcims inherit this class
    # Defines the interface for dcims
    # and implements basic functionality
    def __init__(self, identifier, api_url):
        self.identifier = identifier
        self.api_url = api_url

    def get_info(self):
        raise NotImplementedError("get_info not implemented")

    def get_oobs(self):
        raise NotImplementedError("get_oobs not implemented")

class DcimError(Exception):
    pass
