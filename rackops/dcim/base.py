class DcimBase(object):
    # All dcims inherit this class
    # Defines the interface for dcims
    # and implements basic functionality
    def __init__(self, identifier, is_rack, is_rack_unit, is_serial, api_url):
        self.identifier = identifier
        self.api_url = api_url
        self.is_rack = is_rack
        self.is_rack_unit = is_rack_unit
        self.is_serial = is_serial

    def get_info(self):
        raise NotImplementedError("get_info not implemented")

    def get_oobs(self):
        raise NotImplementedError("get_oobs not implemented")

class DcimError(Exception):
    pass
