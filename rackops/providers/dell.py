import re
import sys
import time
import pexpect

from subprocess import Popen
from rackops.providers.base import ProviderBase

class Dell(ProviderBase):
    def console(self):
        ipmi_host = self.host.get_ipmi_host()
        try:
            Popen(['moob', '-u', '{}'.format(self.username),
                  '-p', '{}'.format(self.password), '-m', ipmi_host.replace("https://", "")])
        except OSError:
            print('Please "apt-get install libcurl4-openssl-dev"\
                   then "gem install moob"')
            sys.exit(10)

    def _ssh(self, command):
        # performs command using ssh
        # returns decoded output

        host  = self.host.get_ipmi_host().replace("https://", "")
        ssh_newkey = 'Are you sure you want to continue connecting'
        prompt = 'ssh -o PubkeyAuthentication=no {}{}  {} '.format(self.username + "@", host, command)

        # returns output
        output = None
        password_str = "password:"
        expected = [ssh_newkey, password_str, pexpect.EOF]

        try:
            p = pexpect.spawn(prompt)
            # loop through expected outputs
            # till EOF is reached
            while (1):
                i = p.expect(expected)
                if expected[i] == ssh_newkey:
                    p.sendline('yes')
                if expected[i] == password_str:
                    p.sendline(self.password)
                    output = p.read()
                if expected[i] == pexpect.EOF:
                    break
        except pexpect.TIMEOUT:
            print('Connection timeout while connecting to idrac')
            sys.exit(10)

        if not output:
            print ("Cannot retrieve output. Exiting...")
            sys.exit(10)

        return output.decode("utf-8")


    def _find_jid(self, output):
        try:
            return re.search(r"JID_.*", output).group(0)
        except AttributeError:
            print("No Job ID found.\nCommand output: ", output)
            sys.exit(10)

    def _confirm_job(self, jid):
        try:
            re.search(r"Job completed successfully", jid).group(0)
        except AttributeError:
            print("Job did not complete successfully.\nCommand output: ", jid)
            sys.exit(10)

    def diagnostics(self):
        jobqueue_view = 'racadm jobqueue view -i {}'
        output = self._ssh('racadm techsupreport collect')
        jid = self._find_jid(output)
        time.sleep(180) # wait 3 minutes to collect the TSR report
        view_output = self._ssh(jobqueue_view.format(jid))
        self._confirm_job(view_output)

        output = self._ssh('racadm techsupreport export -l {}'.format(self.nfs_share))
        jid = self._find_jid(output)
        view_output = self._ssh(jobqueue_view.format(jid))
        self._confirm_job(view_output)
