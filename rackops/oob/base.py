import sys

from subprocess import Popen, check_output, CalledProcessError, call

class OobBase(object):
    URL_LOGIN = '/rpc/WEBSES/create.asp'
    URL_VNC = '/Java/jviewer.jnlp?EXTRNIP={}&JNLPSTR=JViewer'

    # All oobs inherit this class
    # Defines the interface for oobs
    # and implements basic functionality.
    def __init__(self, command, dcim, command_args, username=None, password=None,
        wait=False, force=False, http_share=None, nfs_share=None):
        self.command = command
        self.dcim = dcim
        self.command_args = command_args
        self.username = username
        self.password = password
        self.wait = wait
        self.force = force
        self.nfs_share = nfs_share
        self.http_share = http_share

    def info(self):
        if getattr(self.dcim, "get_short_info", None):
            info = self.dcim.get_short_info()
        else:
            info = self.dcim.get_info()

        for key, val in info.items():
            print (key.replace("_", " ").upper(), ": ", val)


    def open(self):
        try:
            Popen(['open', self.dcim.get_ipmi_host()])
        except:
            sys.stderr.write("Couldn't open browser. Exiting...\n")
            sys.exit(10)

    def _get_ipmi_tool_prefix(self):
        dcim = self.dcim.get_ipmi_host().replace("https://", "")
        return ["ipmitool", "-U", self.username, "-P", self.password,
            "-I", "lanplus", "-H", dcim]

    # command is an array
    def _execute(self, command, output=False):
        prefix = self._get_ipmi_tool_prefix()
        command = prefix + command
        try:
            if output:
                return check_output(command).decode('utf-8')

            call(command)
        except CalledProcessError as e:
            error = "Command %s failed with %s" % (' '.join(command), str(e))
            sys.stderr.write(error)
            sys.exit(10)
        except UnicodeError as e:
            error = "Decoding the output of command %s failed with %s" % (' '.join(command), str(e))
            sys.stderr.write(error)
            sys.exit(10)

    def identify(self):
        if len(self.command_args) != 1:
            print ("Wrong number of args")
            sys.exit(1)

        try:
            blink = int(self.command_args[0])
        except ValueError:
            print ("Argument not an int")
            sys.exit(1)

        print (self._execute(
            ['chassis', 'identify', self.command_args[0]],
            output=True
        ).strip())

    def status(self):
        print (self._execute(
            ['chassis', 'status'],
            output=True
        ).strip())

    def power_status(self):
        print (self._execute(
            ['chassis', 'power', 'status'],
            output=True
        ).strip())

    def power_status(self):
        print (self._execute(
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
        print(self._execute(['sel', 'list'], output=True).strip())

    def console(self):
        raise NotImplementedError("console not implemented in child class")

    def diagnostics(self, nfs_share):
        raise NotImplementedError("diagnostics command is not implemented in child process")

    def autoupdate(self):
        raise NotImplementedError("autoupdate command is not implemented in child process")

    def upgrade(self):
        raise NotImplementedError("upgrade command is not implemented in child process")

    def idrac_info(self):
        raise NotImplementedError("idrac-info command is not implemented in child process")

class OobError(Exception):
    pass
