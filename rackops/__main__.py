import argparse
import json
import os
import sys
import configparser

from rackops.rackops import Rackops
from getpass import getpass

def get_config(config_path):
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
    except configparser.ParsingError as e:
        print ("Invalid configuration file\n")
        sys.exit(1)

    try:
        return config['DEFAULT']
    except:
        print ("No DEFAULT section in configuration file\n")
        sys.exit(1)

def set_environment_variables(config):
    # Read environment variables regarding
    # whatever the config file might include
    if os.environ.get("RACKOPS_USERNAME", None):
        config["username"] = os.environ["RACKOPS_USERNAME"]

    if os.environ.get("RACKOPS_PASSWORD", None):
        config["password"] = os.environ["RACKOPS_PASSWORD"]

    if os.environ.get("RACKOPS_DCIM", None):
        config["dcim"] = os.environ["RACKOPS_DCIM"]

    if os.environ.get("RACKOPS_API_URL", None):
        config["api_url"] = os.environ["RACKOPS_API_URL"]

    if os.environ.get("RACKOPS_NFS_SHARE", None):
        config["nfs_share"] = os.environ["RACKOPS_NFS_SHARE"]

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
        "-c",
        "--config",
        action="store",
        help="Configuration file path",
        default=default_config_path
    )
    parser.add_argument(
        "command",
        help="Command which will be executed"
    )
    parser.add_argument(
        "identifier",
        help="Identifier for the machine which the command will be executed"
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
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose",
        default=False
    )
    args = parser.parse_args()

    config = get_config(args.config)
    # if no configuration file was found initialize an empty config
    if not config:
        config = {}

    set_environment_variables(config)

    if args.username:
        config["username"] = args.username

    if not config.get("username", None):
        config["username"] = input("Please provide an IPMI username: ")

    if not config.get("dcim", None):
        config["dcim"] = "netbox"

    if args.password and args.password != True:
        config["password"] = args.password
    elif args.password == True or not config.get("password", None):
        config["password"] = getpass("Please provide an IPMI password: ")

    config['force'] = args.force
    config['wait'] = args.wait
    config['verbose'] = args.verbose

    rackops = Rackops(args.command, args.identifier, config)
    rackops.run()

if __name__ == "__main__":
    main()
