from getpass import getpass

from rackops.dcim.netbox import Netbox

from rackops.oob.lenovo import Lenovo
from rackops.oob.dell import Dell
from rackops.oob.fujitsu import Fujitsu

class Rackops:
    COMMANDS = ["info", "console", "open", "status", "ssh",
        "idrac-info", "autoupdate", "upgrade", "diagnostics"
        "power-status", "power-on", "power-off", "power-cycle", "power-reset",
        "boot-pxe", "boot-local",
        "ipmi-reset", "ipmi-logs"]
    def __init__(self, command, identifier, args, config, env_vars):
        if command not in self.COMMANDS:
            raise RackopsError("Invalid command")
        self.command = command
        self.identifier = identifier
        self.args = args
        self.config = config
        self.env_vars = env_vars

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
        dcim_params = self.config[self.args.dcim.lower()]
        try:
            return self._dcim_table()[self.args.dcim](self.identifier, dcim_params['api_url'])
        except KeyError:
            raise RackopsError("Not a valid dcim")

    def _get_oob_params(self, oob):
        config = {}
        oob_params = self.config[oob.lower()]
        env_vars = self.env_vars
        if self.args.username:
            config['username'] = self.args.username
        elif env_vars.get('username', None):
            config['username'] = env_vars['username']
        elif oob_params.get('username', None):
            config['username'] = oob_params['username']
        else:
            config["username"] = input("Please provide an IPMI username: ")

        if self.args.password and self.args.password != True:
            config['password'] = self.args.password
        elif self.args.password:
            config["password"] = getpass("Please provide an IPMI password: ")
        elif oob_params.get('password', None):
            config['password'] = oob_params['password']
        else:
            config["password"] = getpass("Please provide an IPMI password: ")

        config['nfs_share'] = False
        if oob_params.get('nfs_share', None) or env_vars.get('nfs_share', None):
            config['nfs_share'] = True

        config['http_share'] = False
        if env_vars.get('http_share', None):
            config['http_share'] =env_vars['http_share']
        elif dcim_section.get('http_share', None):
            config['http_share'] = dcim_section['http_share']

        return config

    def _get_oob(self, dcim):
        oob = dcim.get_oob()
        params = self._get_oob_params(oob)
        try:
            return self._oobs_table()[oob](
                self.command,
                dcim,
                username=params["username"],
                password=params["password"],
                nfs_share=params["nfs_share"],
                http_share=params["http_share"],
                force=self.args.force,
                wait=self.args.wait
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
