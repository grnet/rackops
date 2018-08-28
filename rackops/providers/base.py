class ProviderBase(object):
    URL_LOGIN = '/rpc/WEBSES/create.asp'
    URL_VNC = '/Java/jviewer.jnlp?EXTRNIP={}&JNLPSTR=JViewer'

    # All providers inherit this class
    # Defines the interface for providers
    # and implements basic functionality.
    def __init__(self, command, host, username=None, password=None):
        self.command = command
        self.host = host
        self.username = username
        self.password = password

    def info(self):
        raise NotImplementedError("info not implemented in child class")

    def console(self):
        raise NotImplementedError("console not implemented in child class")

    def shutdown(self):
        raise NotImplementedError("shutdown not implemented in child class")


class ProviderError(Exception):
    pass
