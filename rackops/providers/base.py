import sys

from subprocess import Popen, check_output, CalledProcessError, call

class ProviderBase(object):
    URL_LOGIN = '/rpc/WEBSES/create.asp'
    URL_VNC = '/Java/jviewer.jnlp?EXTRNIP={}&JNLPSTR=JViewer'

    # All providers inherit this class
    # Defines the interface for providers
    # and implements basic functionality.
    def __init__(self, command, host, username=None, password=None,
        verbose=False, wait=False, force=False, nfs_share=None):
        self.command = command
        self.host = host
        self.username = username
        self.password = password
        self.verbose = verbose
        self.wait = wait
        self.force = force
        self.nfs_share = nfs_share

    def info(self):
        if getattr(self.host, "get_short_info", None):
            info = self.host.get_short_info()
        else:
            info = self.host.get_info()

        for key, val in info.items():
            print (key.replace("_", " ").upper(), ": ", val)

    def open(self):
        try:
            Popen(['open', self.host.get_ipmi_host()])
        except:
            sys.stderr.write("Couldn't open browser. Exiting...\n")
            sys.exit(10)

    def _get_ipmi_tool_prefix(self):
        host = self.host.get_ipmi_host().replace("https://", "")
        return ["ipmitool", "-U", self.username, "-P", self.password,
            "-I", "lanplus", "-H", host]

    # command is an array
    def _execute(self, command, output=False):
        prefix = self._get_ipmi_tool_prefix()
        command = prefix + command
        try:
            if self.verbose:
                print ("Executing:\n%s" % ' '.join(command))
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

class ProviderError(Exception):
    pass
