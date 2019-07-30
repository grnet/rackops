import re
import sys
import time
import paramiko
import logging

from subprocess import Popen
from rackops.oob.base import OobBase

class Dell(OobBase):
    def console(self):
        ipmi_host = self.oob_info["ipmi"]
        try:
            Popen(['moob', '-u', '{}'.format(self.username),
                  '-p', '{}'.format(self.password), '-m', ipmi_host.replace("https://", "")])
        except OSError:
            print('Please run "gem install moob"')
            sys.exit(10)

    def _ssh(self, command):
        # performs command using ssh
        # returns decoded output

        nbytes = 4096
        port = 22
        hostname = self.oob_info["ipmi"].replace("https://", "")
        username = self.username
        password = self.password

        client = paramiko.Transport((hostname, port))
        client.connect(username=username, password=password)
        stdout_data = []
        stderr_data = []
        session = client.open_channel(kind='session')
        session.exec_command(command)
        while True:
            if session.recv_ready():
                stdout_data.append(session.recv(nbytes))
            if session.recv_stderr_ready():
                stderr_data.append(session.recv_stderr(nbytes))
            if session.exit_status_ready():
                break
        output = b''.join(stdout_data)
        session.close()
        client.close()

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
        logging.info("Sleeping for 3 minutes to collect the TSR report")
        time.sleep(180) # wait 3 minutes to collect the TSR report
        view_output = self._ssh(jobqueue_view.format(jid))
        self._confirm_job(view_output)
        output = self._ssh('racadm techsupreport export -l {}'.format(self.nfs_share))
        jid = self._find_jid(output)
        view_output = self._ssh(jobqueue_view.format(jid))
        self._confirm_job(view_output)

    def autoupdate(self):
        jobqueue_view = 'racadm jobqueue view -i {}'
        schedule_updates = ("racadm autoupdatescheduler create -l {} "
                "-f grnet_1.00_Catalog.xml -a 0 -time 08:30"
                "-dom * -wom * -dow * -rp 1").format(self.http_share)
        enable_updates = 'racadm set lifecycleController.lcattributes.AutoUpdate Enabled'
        enable_updates_output = self._ssh(enable_updates)
        schedule_updates_output = self._ssh(schedule_updates)
        print(enable_updates_output)
        print(schedule_updates_output)

    def upgrade(self):
        http_addr = self.http_share.strip('http:/')
        upgrade = 'racadm update -f grnet_1.00_Catalog.xml -e {} -t HTTP -a FALSE'.format(http_addr)
        output = self._ssh(upgrade)

    def idrac_info(self):
        firm_info = 'racadm get idrac.info'
        bios_info = 'racadm get bios.sysinformation'
        print(self._ssh(firm_info))
        print(self._ssh(bios_info))

    def clear_autoupdate(self):
        clear_command = 'racadm autoupdatescheduler clear'
        print(self._ssh(clear_command))
