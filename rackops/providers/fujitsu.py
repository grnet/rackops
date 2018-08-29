try:
    # Python 3
    from urllib import request
    from urllib import error as urlerror
except ImportError:
    # Python 2
    import urllib2 as request
    urlerror = request

import sys
import re
import tempfile

from bs4 import BeautifulSoup
from subprocess import Popen

from rackops.providers.base import ProviderBase

class Fujitsu(ProviderBase):
    def _get_realm(self):
        """does an unauthenticated request to get the real for auth afterwards."""
        opener = request.build_opener()
        request.install_opener(opener)
        try:
            request.urlopen(self.host.get_ipmi_host())
        #except Exception as err:
        except urlerror.HTTPError as err:
            header = err.headers.get('WWW-Authenticate')
            m = re.match('Digest realm="([@\w\s-]+)",', header)
            realm = m.groups()[0]
        return realm

    def _install_auth(self):
        """setup digest auth"""
        realm = self._get_realm()

        uri = self.host.get_ipmi_host()
        username = self.username
        password = self.password

        auth_handler = request.HTTPDigestAuthHandler()
        auth_handler.add_password(realm=realm,
                                  uri=uri, user=username, passwd=password)
        opener = request.build_opener(auth_handler)
        request.install_opener(opener)

    def _find_avr_url(self):
        """Parse the main page to find the url for the jws"""
        url = self.host.get_ipmi_host()

        req = request.Request(url)
        data = request.urlopen(req).read()
        soup = BeautifulSoup(data)
        jnlp_desc = [u'Video Redirection (JWS)']
        links = soup.find_all('a', href=True)
        for link in links:
            if link.contents == jnlp_desc:
                return url + "/" + link['href']

    def _save_tmp_jnlp(self):
        """ Fetch the xml jnlp file and save in tmp"""
        avr_url = self._find_avr_url()
        resource = request.urlopen(request.Request(avr_url))
        xml_data = resource.read().decode('utf-8')
        _, tmppath = tempfile.mkstemp()
        with open(tmppath, 'w') as tmpfile:
            tmpfile.write(xml_data)
        return tmppath

    def console(self):
        self._install_auth()
        avr_file = self._save_tmp_jnlp()
        Popen(['/usr/bin/javaws', avr_file])
