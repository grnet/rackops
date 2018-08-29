rackops is a tool for performing operations on rack operations.

It currently supports Netbox hosts and the Lenovo, Fujitsu, Dell providers.

To add a host or provider read CONTRIBUTING.md.

Installation
============

1. Clone the repository.
2. On the root directory perform `python3 setup.py install`

Configuration
=============

rackops uses a JSON configuration file.
It defaults to `~/.rackopsrc`, but a different configuration file
can be used using the `-c` command line argument.

The configuration file should have this form:
```
{
    "host": <host>,
    "api_url": <api_url>,
    "username": <urername>,
    "password": <password>
}
```

where:
- `host` is the name of your host. Currently `host` can only be `"netbox"`.
- `api_url` is the URL of your host's API (i.e.
  https://netbox.noc.grnet.gr/api/dcim/devices/)
- `username` is the username that will be used while connecting to a provider,
  while
- `password` is the password that will be used

If environment variables for the above values are defined, they will overwrite
those from the configuration file. The environment variables supported are:

- `RACKOPS_USERNAME`
- `RACKOPS_PASSWORD`
- `RACKOPS_HOST`
- `RACKOPS_API_URL`

If command line arguments for the username and password are defined, they will overwrite
those from the configuration file and the environment variables.

Usage
=====

rackops can work as a CLI module or a python3 module.


CLI
---

`rackops <command> <identifier>`

The non-required command line arguments are:

- `-c`,`--config`. The location of the configuration file.
- `-u`, `--username`
- `-p`, `--password`. With this argument if the password is not provided as a string,
    the user will be prompted for entering a password.


As a module
-----------

1. `from rackops.rackops import Rackops`
2. `rackops = Rackops(command, identifier, config)`. `config` should be a hash
   table with the values defined in the *Configuration* section.
3. `rackops.run()`
