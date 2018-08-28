import argparse
import json
import os

from rackops import Rackops
from getpass import getpass

def get_config(config_path):
    try:
        with open(os.path.abspath(config_path), "r") as f:
            contents = f.read()
    except (OSError, IOError) as e:
        # no configuration file found
        return None

    try:
        contents = json.loads(contents)
    except ValueError as e:
        print "Configuration file %s doesn't contain valid JSON" % (config_path)
        exit(1)

    return contents

def set_environment_variables(config):
    # Read environment variables regarding
    # whatever the config file might include
    if os.environ.get("RACKOPS_USERNAME", None):
        config["username"] = os.environ["RACKOPS_USERNAME"]

    if os.environ.get("RACKOPS_PASSWORD", None):
        config["password"] = os.environ["RACKOPS_PASSWORD"]

    if os.environ.get("RACKOPS_HOST", None):
        config["host"] = os.environ["RACKOPS_HOST"]

    if os.environ.get("RACKOPS_API_URL", None):
        config["api_url"] = os.environ["RACKOPS_API_URL"]


def main():
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
        default=os.path.join(os.environ.get("HOME", "/"), ".rackopsrc")
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
    args = parser.parse_args()

    config = get_config(args.config)

    # if no configuration file was found initialize an empty config
    if not config:
        config = {}

    set_environment_variables(config)

    if args.username:
        config["username"] = args.username

    if not config.get("username", None):
        config["username"] = raw_input("Please provide an IPMI username\n")

    if args.password and args.password != True:
        config["password"] = args.password
    elif args.password == True or not config.get("password", None):
        config["password"] = getpass("Please provide an IPMI password\n")

    rackops = Rackops(args.command, args.identifier, config)
    rackops.run()

if __name__ == "__main__":
    main()
