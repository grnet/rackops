import sys

from subprocess import Popen
from providers.base import ProviderBase

class Dell(ProviderBase):
    def console(self):
        ipmi_host = self.host.get_ipmi_host()

        try:
            Popen(['moob', '-u', '{}'.format(self.username),
                  '-p', '{}'.format(self.password), '-m', ipmi_host.replace("https://", "http://")])
        except OSError:
            print('Please "apt-get install libcurl4-openssl-dev"\
                   then "gem install moob"')
            sys.exit(10)
