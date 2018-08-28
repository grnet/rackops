import urllib
import sys
import re
import tempfile

from bs4 import BeautifulSoup
from subprocess import Popen

from providers.base import ProviderBase

class Fujitsu(ProviderBase):
    def _get_realm(self):
        """does an unauthenticated request to get the real for auth afterwards."""
        opener = urllib.build_opener()
        urllib.install_opener(opener)
        try:
            urllib.urlopen(self.host.get_ipmi_host())
        #except Exception as err:
        except urllib.HTTPError as err:
            header = err.headers.getheader('WWW-Authenticate')
            m = re.match('Digest realm="([@\w\s-]+)",', header)
            realm = m.groups()[0]
        return realm

    def _install_auth(self):
        """setup digest auth"""
        realm = self._get_realm()

        uri = self.host.get_ipmi_host()
        username = self.username
        password = self.password

        auth_handler = urllib.HTTPDigestAuthHandler()
        auth_handler.add_password(realm=realm,
                                  uri=uri, user=username, passwd=password)
        opener = urllib.build_opener(auth_handler)
        urllib.install_opener(opener)

    def _find_avr_url(self):
        """Parse the main page to find the url for the jws"""
        url = self.host.get_ipmi_host()

        req = urllib.Request(url)
        data = urllib.urlopen(req).read()
        soup = BeautifulSoup(data)
        jnlp_desc = [u'Video Redirection (JWS)']
        links = soup.find_all('a', href=True)
        for link in links:
            if link.contents == jnlp_desc:
                return url + "/" + link['href']

    def _save_tmp_jnlp(self):
        """ Fetch the xml jnlp file and save in tmp"""
        avr_url = self._find_avr_url()
        xml_data = urllib.urlopen(urllib.Request(avr_url)).read()
        _, tmppath = tempfile.mkstemp()
        with open(tmppath, 'w') as tmpfile:
            tmpfile.write(xml_data)
        return tmppath

    def console(self):
        self._install_auth()
        avr_file = self._save_tmp_jnlp()
        Popen(['/usr/bin/javaws', avr_file])
