rackops is a tool for performing operations on rack operations.

It currently supports Netbox hosts and the Lenovo, Fujitsu, Dell providers.

To add a host or provider read [CONTRIBUTING.md](docs/CONTRIBUTING.md).

Installation
============

1. Clone the repository.
2. `apt-get install python3-setuptools python3-requests python3-bs4
   python3-slimit python3-distutils python3-paramiko python3-paramiko
   libcurl4-openssl-dev`
3. On the root directory perform `sudo python3 setup.py install`

Configuration
=============

rackops uses a JSON configuration file.
It defaults to `~/.config/rackops` or `$XDG_CONFIG_HOME/rackops` if
the environment variable `$XDG_CONFIG_HOME` is set,
but a different configuration file can be used
using the `-c` command line argument.

We use the [configparser](https://docs.python.org/3/library/configparser.html)
module for configuration parsing.

The configuration file should have this form:
```
[<DCIM1>]
api_url = <api_url1>

[<DCIM2>]
api_url = <api_url2>

[<OOB1>]
username = <oob1_username>
password = <oob1_password>
nfs_share = "IP:/path/"
http_share = "http://IP/path/"

[<OOB2>]
username = <oob2_username>
password = <oob2_password>
nfs_share = "IP:/path/"
http_share = "http://IP/path/"
```

where:
- `<DCIM>` is the name of a dcim. Currently we only support the `netbox` dcim.
- `<api_url>` is the API URL of the specified DCIM.
  (i.e https://netbox.noc.grnet.gr/)
- `<OOB>` is the name of an oob (i.e. lenovo)
- `<username>` is the username associated with a specific oob.
  while
- `<password>` is the password that will be used for a specific oob.
- `nfs_share` is the nfs share where diagnostics from Dell hosts are uploaded,
- `http_share` is an http share where Dell hosts retrieve idrac updates from,

If environment variables for the above values are defined, they will overwrite
those from the configuration file. The environment variables supported are:

- `RACKOPS_USERNAME`
- `RACKOPS_PASSWORD`
- `RACKOPS_NFS_SHARE`
- `RACKOPS_HTTP_SHARE`

If command line arguments for the username and password are defined, they will overwrite
those from the configuration file and the environment variables.

Usage
=====

rackops can work as a CLI module or a python3 module.


CLI
---

`rackops <command> <identifier>`

The non-required command line arguments are:

- `-d`, `--dcim`. Name of the DCIM to be used. Defaults to `netbox`.
- `-r`, `--rack`. The identifier provided is an identifier for a rack.
- `-a`, `--rack-unit`. The identifier provided is an identifier for a rack
  unit.
- `-s`, `--serial`. The identifier provided is an identifier for a serial.
- `-c`,`--config`. The location of the configuration file.
- `-u`, `--username`
- `-p`, `--password`. With this argument if the password is not provided as a string,
    the user will be prompted for entering a password.
- `-f`, `--force`. Some commands can be run with this argument. See `Commands`
  for more details.
- `-w`, `--wait`. Some commands can be run with this argument. See `Commands`
  for more details.
- `-v`, `--verbose`. Set log level to INFO, and DEBUG for `-vv`.


As a module
-----------

1. `from rackops.rackops import Rackops`
2. `rackops = Rackops(command, identifier, is_rack, is_rack_unit, is_serial,
   command_args, args, config, environment_variables)`. `config` should be a hash
   table with the values defined in the *Configuration* section.
   `args` should be a hash map containing the command line arguments specified
   above as keys (i.e. {"wait": True})
   `is_rack`, `is_rack_unit`, `is_serial` are boolean values specifying if the
   identifier corresponds to a rack, rack unit or serial respectivelly.
   `command_args` is a list containing arguments for the command to be run.
   `environment_variables` is a hash map containing the environment variables
   specified above.
3. `rackops.run()`

Commands
--------

- `info`: Print information regarding the machine.
- `console`: Opens a Java console on the remote machine.
- `open`: Opens the IPMI host url on the client machine.
- `status`: Prints information regarding the status of the remote machine.
- `power-status`: Prints whether the machine is on/off.
- `power-on`: Powers on the machine.
- `power-off`: Sends a signal to the operating system for shutoff.
    Can be run with the `--force` command line argument for a hard shutoff.
    Can be run with the `--wait` argument to wait until the operating system
    shutoff is complete before exiting.
- `power-cycle`: Soft restart.
- `power-reset`: Hard restart.
- `boot-pxe`: Force pxe boot.
- `boot-local`: Force boot from default harddrive.
- `ipmi-reset`: Restart ipmi device. Can be run with the `--force` command line
  argument for resetting the ipmi device.
- `ipmi-logs`: Print system event logs.
- `diagnostics` : Initiate diagnostics report on Dell ipmi and export it to an
    nfs share
- `autoupdate`: Schedule auto updates on a Dell host every day at 08:30
- `upgrade`: Instantly update an iDrac's firmware from an http share
- `idrac-info`: Receive BIOS version and controller info from an iDrac
