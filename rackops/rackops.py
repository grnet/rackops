from rackops.dcim.netbox import Netbox

from rackops.oob.lenovo import Lenovo
from rackops.oob.dell import Dell
from rackops.oob.fujitsu import Fujitsu

class Rackops:
    COMMANDS = ["info", "console", "open", "status",
        "power-status", "power-on", "power-off", "power-cycle", "power-reset",
        "boot-pxe", "boot-local", "ipmi-reset", "ipmi-logs",
        "idrac-info", "autoupdate", "upgrade", "diagnostics"]
    def __init__(self, command, identifier, config):
        self.command = command
        self.identifier = identifier
        self.config = config
        if command not in self.COMMANDS:
            raise RackopsError("Invalid command")

    def _dcim_table(self):
        return {
            'netbox': Netbox
        }

    def _oobs_table(self):
        return {
            'lenovo': Lenovo,
            'dell': Dell,
            'dell-inc': Dell,
            'fujitsu': Fujitsu
        }

    def _get_dcim(self):
        dcim = self.config["dcim"].lower()
        api_url = self.config["api_url"]
        try:
            return self._dcim_table()[dcim](self.identifier, api_url)
        except KeyError:
            raise RackopsError("Not a valid dcim")

    def _get_oob(self, dcim):
        oob = dcim.get_oob()
        try:
            return self._oobs_table()[oob](
                self.command,
                dcim,
                username=self.config["username"],
                password=self.config["password"],
                nfs_share=self.config["nfs_share"],
                http_share=self.config["http_share"],
                force=self.config.get("force", False),
                wait=self.config.get("wait", False)
            )
        except KeyError:
            raise RackopsError("Not a valid oob")

    def run(self):
        # Controller.
        # Needs to find the correct dcim and the correct oob
        dcim = self._get_dcim()
        oob = self._get_oob(dcim)

        getattr(oob, self.command.replace("-", "_"))()

class RackopsError(Exception):
    pass
