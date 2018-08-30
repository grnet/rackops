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
        if getattr(self.host, "get_short_info", None):
            info = self.host.get_short_info()
        else:
            info = self.host.get_info()

        for key, val in info.iteritems():
            print (key.replace("_", " ").upper(), ": ", val)

    def console(self):
        raise NotImplementedError("console not implemented in child class")



class ProviderError(Exception):
    pass
