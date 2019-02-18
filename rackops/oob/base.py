import sys
import logging

from subprocess import Popen, check_output, CalledProcessError, call

class OobBase(object):
    URL_LOGIN = '/rpc/WEBSES/create.asp'
    URL_VNC = '/Java/jviewer.jnlp?EXTRNIP={}&JNLPSTR=JViewer'

    # All oobs inherit this class
    # Defines the interface for oobs
    # and implements basic functionality.
    def __init__(self, command, oob_info, command_args, username=None, password=None,
        wait=False, force=False, http_share=None, nfs_share=None):
        self.command = command
        self.oob_info = oob_info
        self.command_args = command_args
        self.username = username
        self.password = password
        self.wait = wait
        self.force = force
        self.nfs_share = nfs_share
        self.http_share = http_share

    def _print(self, msg):
        sys.stdout.write("{}:\n{}\n".format(self.oob_info["identifier"], msg))

    def info(self):
        logging.info("Executing info")
        info = self.oob_info["info"]

        info_str = ""
        for key, val in info.items():
            info_str += ("{}:{}\n".format(key.replace("_", " ").upper(), val))

        self._print(info_str[:-1])


    def _execute_popen(self, command):
        logging.info("Executing {}".format(" ".join(command)))
        try:
            Popen(command)
        except:
            raise OobError("Couldn't open browser" \
                "with command {}. Exiting...".format(" ".join(command)))

    def open(self):
        self._execute_popen(['open', self.oob_info["ipmi"]])

    def ssh(self):
        status_command = ['chassis', 'power', 'status']
        if self.wait:
            if 'off' in self._execute(status_command, output=True):
                logging.info("Waiting for machine to turn on...")

            while (1):
                if 'off' not in self._execute(status_command, output=True):
                    break

        host = self.oob_info["asset_tag"]
        if not host:
            raise OobError("Can't perform ssh without an asset tag")
        call(['ssh', host])

    def _get_ipmi_tool_prefix(self):
        host = self.oob_info["ipmi"].replace("https://", "")
        return ["ipmitool", "-U", self.username, "-P", self.password,
            "-I", "lanplus", "-H", host]

    # command is an array
    def _execute(self, command, output=False):
        if not self.oob_info["ipmi"]:
            logging.warn("oob {} doesn't contain an IPMI field".format(self.oob_info["oob"]))
            return ""

        prefix = self._get_ipmi_tool_prefix()
        command = prefix + command
        logging.info("Executing {}".format(" ".join(command)))
        try:
            if output:
                return check_output(command).decode('utf-8')

            call(command)
        except CalledProcessError as e:
            error = "Command %s failed with %s" % (' '.join(command), str(e))
            raise OobError(error)
        except UnicodeError as e:
            error = "Decoding the output of command %s failed with %s" % (' '.join(command), str(e))
            raise OobError(error)

    def identify(self):
        if len(self.command_args) != 1:
            raise OobError("Wrong number of args")

        try:
            blink = int(self.command_args[0])
        except ValueError:
            raise OobError("Argument not an int")

        self._print(self._execute(
            ['chassis', 'identify', self.command_args[0]],
            output=True
        ).strip())

    def status(self):
        self._print(self._execute(
            ['chassis', 'status'],
            output=True
        ).strip())

    def power_status(self):
        self._print(self._execute(
            ['chassis', 'power', 'status'],
            output=True
        ).strip())

    def power_status(self):
        self._print(self._execute(
            ['chassis', 'power', 'status'],
            output=True
        ).strip())

    def power_on(self):
        self._execute(['chassis', 'power', 'on'])

    def power_off(self):
        cmd = ['chassis', 'power']
        if self.force:
            cmd.append('off')
        else:
            cmd.append('soft')
        self._execute(cmd)
        if self.wait:
            while (1):
                if 'off' in self._execute(['chassis', 'power', 'status'], output=True):
                    break

    def power_cycle(self):
        self._execute(['chassis', 'power', 'cycle'])

    def power_reset(self):
        self._execute(['chassis', 'power', 'reset'])

    def boot_pxe(self):
        self._execute(['chassis', 'bootdev', 'pxe'])

    def boot_local(self):
        self._execute(['chassis', 'bootdev', 'disk'])

    def ipmi_reset(self):
        cmd = ['mc', 'reset']
        if self.force:
            cmd.append('cold')
        else:
            cmd.append('warm')

        self._execute(cmd)

    def ipmi_logs(self):
        self._print(self._execute(['sel', 'list'], output=True).strip())

    def console(self):
        raise NotImplementedError("console not implemented in child class")

    def diagnostics(self):
        raise NotImplementedError("diagnostics command is not implemented in child process")

    def autoupdate(self):
        raise NotImplementedError("autoupdate command is not implemented in child process")

    def upgrade(self):
        raise NotImplementedError("upgrade command is not implemented in child process")

    def idrac_info(self):
        raise NotImplementedError("idrac-info command is not implemented in child process")

class OobError(Exception):
    pass
