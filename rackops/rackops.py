from getpass import getpass

from rackops.dcim.netbox import Netbox

from rackops.oob.lenovo import Lenovo
from rackops.oob.dell import Dell
from rackops.oob.fujitsu import Fujitsu

class Rackops:
    COMMANDS = ["info", "console", "open", "status",
        "idrac-info", "autoupdate", "upgrade", "diagnostics"
        "power-status", "power-on", "power-off", "power-cycle", "power-reset",
        "boot-pxe", "boot-local",
        "ipmi-reset", "ipmi-logs"]
    def __init__(self, command, identifier, args, config, env_vars):
        self.command = command
        self.identifier = identifier
        self.args = args
        self.config = config
        self.env_vars = env_vars
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

    def _get_dcim_params(self):
        dcim_section = self.config[self.args.dcim.upper()]
        return {'api_url': dcim_section['api_url']}

    def _get_dcim(self):
        params = self._get_dcim_params()
        try:
            return self._dcim_table()[self.args.dcim](self.identifier, params['api_url'])
        except KeyError:
            raise RackopsError("Not a valid dcim")

    def _get_oob_params(self, oob):
        config = {}
        dcim_section = self.config[oob.upper()]
        env_vars = self.env_vars
        if self.args.username:
            config['username'] = self.args.username
        elif env_vars.get('username', None):
            config['username'] = env_vars['username']
        elif dcim_section.get('username', None):
            config['username'] = dcim_section['username']
        else:
            config["username"] = input("Please provide an IPMI username: ")

        if self.args.password and self.args.password != True:
            config['password'] = self.args.password
        elif self.args.password:
            config["password"] = getpass("Please provide an IPMI password: ")
        elif dcim_section.get('password', None):
            config['password'] = dcim_section['password']
        else:
            config["password"] = getpass("Please provide an IPMI password: ")

        config['nfs_share'] = False
        if dcim_section.get('nfs_share', None):
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
