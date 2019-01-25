import argparse
import json
import os
import sys
import configparser

from rackops.rackops import Rackops
from getpass import getpass

def format_config(config):
    # Recursive function that converts a
    # configparser.ConfigParser object into a dict
    # Can't convert directly with dict(config)
    # since dict(config) returns the dict in the form:
    # {"section_1": "<Section1 Object>", "section_2": "<Section2 Object, ...}
    # but using dict(config["section_1"]) we can see a valid dict representation
    # of the specified section.
    # so this basically recursivelly calls dict() on every subdict
    keys = dict(config).keys()
    formatted = {}
    for k in keys:
        formatted[k.lower()] = config[k]
        if not type(config[k]) == str:
            formatted[k.lower()] = format_config(config[k])
    return formatted

def get_config(config_path):
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
    except configparser.ParsingError as e:
        print ("Invalid configuration file\n")
        sys.exit(1)

    print (format_config(config))
    exit(1)

def get_environment_variables():
    # Read environment variables regarding
    # whatever the config file might include
    env_vars = {}
    if os.environ.get("RACKOPS_USERNAME", None):
        env_vars["username"] = os.environ["RACKOPS_USERNAME"]

    if os.environ.get("RACKOPS_PASSWORD", None):
        env_vars["password"] = os.environ["RACKOPS_PASSWORD"]

    if os.environ.get("RACKOPS_DCIM", None):
        env_vars["dcim"] = os.environ["RACKOPS_DCIM"]

    if os.environ.get("RACKOPS_NFS_SHARE", None):
        env_vars["nfs_share"] = os.environ["RACKOPS_NFS_SHARE"]

    return env_vars

    if os.environ.get("RACKOPS_HTTP_SHARE", None):
        config["http_share"] = os.environ["RACKOPS_http_SHARE"]

def main():
    default_config_path = os.path.join(os.environ.get("HOME", "/"), ".config", "rackops")
    if os.environ.get("XDG_CONFIG_HOME", None):
        default_config_path = os.environ["XDG_CONFIG_HOME"]
    # 1. Configuration:
    #   - If config file exists, use it
    #   - Else if environment variables exist use those
    #   - Else if command line arguments exist, use those
    #   - Else prompt the user for variables
    # 2. Initialize a Rackops object
    # 3. call rackops.run()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        help="Command which will be executed"
    )
    parser.add_argument(
        "identifier",
        help="Identifier for the machine which the command will be executed"
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        help="Configuration file path",
        default=default_config_path
    )
    parser.add_argument(
        "-u",
        "--username",
        action="store",
        help="IPMI username",
        default=None
    )
    parser.add_argument(
        "-p",
        "--password",
        action="store_true",
        help="IPMI password",
        default=None
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force",
        default=None
    )
    parser.add_argument(
        "-w",
        "--wait",
        action="store_true",
        help="Wait",
        default=None
    )
    parser.add_argument(
        "-d",
        "--dcim",
        help="DCIM name",
        default="netbox"
    )
    args = parser.parse_args()

    config = get_config(args.config)
    env_vars = get_environment_variables()

    rackops = Rackops(args.command, args.identifier, args, config, env_vars)
    rackops.run()

if __name__ == "__main__":
    main()
