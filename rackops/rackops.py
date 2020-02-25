import logging

from getpass import getpass

from rackops.dcim.netbox import Netbox

from rackops.oob.lenovo import Lenovo
from rackops.oob.dell import Dell
from rackops.oob.fujitsu import Fujitsu

class Rackops:
    COMMANDS = ["info", "console", "open", "status", "ssh",
        "idrac-info", "autoupdate", "upgrade", "diagnostics",
        "power-status", "power-on", "power-off", "power-cycle", "power-reset",
        "boot-pxe", "boot-local",
        "ipmi-reset", "ipmi-logs", "clear-autoupdate", "flush-jobs",
        "pdisks-status", "storage-status", "controllers-status"]
    def __init__(self, command, identifier, rack, rack_unit, serial, command_args, args, config, env_vars):
        if command not in self.COMMANDS:
            raise RackopsError("Invalid command")
        self.command = command
        self.identifier = identifier
        self.rack = rack
        self.rack_unit = rack_unit
        self.serial = serial
        self.args = args
        self.config = config
        self.env_vars = env_vars
        self.command_args = command_args

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

    def _config_table(self):
        return {
            'lenovo': 'lenovo',
            'dell': 'dell',
            'dell-inc': 'dell',
            'fujitsu': 'fujitsu'
        }

    def _get_dcim(self):
        dcim = self.args.dcim.lower()
        dcim_params = self.config[dcim]
        try:
            return self._dcim_table()[dcim](self.identifier, self.rack, self.rack_unit, self.serial, dcim_params)
        except KeyError:
            raise RackopsError("Not a valid dcim")

    def _get_oob_params(self, oob):
        config = {}
        try:
            oob_params = self.config[self._config_table()[oob.lower()]]
        except KeyError:
            raise RackopsError("Invalid oob name {}".format(oob))

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

        config['nfs_share'] = None
        if env_vars.get('nfs_share', None):
             config['nfs_share'] = env_vars['nfs_share']
        elif oob_params.get('nfs_share', None):
            config['nfs_share'] = oob_params['nfs_share']

        config['http_share'] = None
        if env_vars.get('http_share', None):
            config['http_share'] = env_vars['http_share']
        elif oob_params.get('http_share', None):
            config['http_share'] = oob_params['http_share']

        return config

    def _execute_command(self, dcim):
        for oob_info in dcim.get_oobs():
            oob = oob_info["oob"]
            params = self._get_oob_params(oob)
            logging.info("Initiating OOB object for oob {}".format(oob))
            try:
                oob_obj = self._oobs_table()[oob](
                    self.command,
                    oob_info,
                    self.command_args,
                    username=params["username"],
                    password=params["password"],
                    nfs_share=params["nfs_share"],
                    http_share=params["http_share"],
                    force=self.args.force,
                    wait=self.args.wait
                )
            except KeyError:
                raise RackopsError("Not a valid oob {}".format(oob))
            command = self.command.replace("-", "_")
            logging.info("Executing command {} on oob {}".format(command, oob))
            getattr(oob_obj, command)()

    def run(self):
        # Controller.
        # Needs to find the correct dcim and the correct oob
        logging.info("Initiating DCIM object")
        dcim = self._get_dcim()
        logging.info("Executing command")
        self._execute_command(dcim)
        logging.info("Done")

class RackopsError(Exception):
    pass
