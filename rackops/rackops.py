from hosts.netbox import Netbox

from providers.lenovo import Lenovo
from providers.dell import Dell
from providers.fujitsu import Fujitsu

class Rackops:
    COMMANDS = ["info", "console"]
    def __init__(self, command, identifier, config):
        self.command = command
        self.identifier = identifier
        self.config = config
        if command not in self.COMMANDS:
            raise RackopsError("Invalid command")

    def _hosts_table(self):
        return {
            'netbox': Netbox
        }

    def _providers_table(self):
        return {
            'lenovo': Lenovo,
            'dell': Dell,
            'dell-inc': Dell,
            'fujitsu': Fujitsu
        }

    def _get_host(self):
        host = self.config["host"].lower()
        api_url = self.config["api_url"]
        try:
            return self._hosts_table()[host](self.identifier, api_url)
        except KeyError:
            raise RackopsError("Not a valid host")

    def _get_provider(self, host):
        provider = host.get_provider()
        try:
            return self._providers_table()[provider](
                self.command,
                host,
                username=self.config["username"],
                password=self.config["password"]
            )
        except KeyError:
            raise RackopsError("Not a valid provider")

    def run(self):
        # Controller.
        # Needs to find the correct host and the correct provider
        host = self._get_host()
        provider = self._get_provider(host)

        getattr(provider, self.command)()

class RackopsError(Exception):
    pass
