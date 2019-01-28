import sys
import tempfile
import slimit
import requests
import re

from rackops.oob.base import OobBase
from subprocess import Popen
from slimit.visitors import nodevisitor

class Lenovo(OobBase):
    def _get_console_cookies(self):
        return {'Cookie': 'Language=EN; SessionExpired=true;'}

    def _get_console_headers(self):
        return {'Content-type': 'text/plain'}

    def _get_console_data(self):
        return {
            "WEBVAR_PASSWORD": str(self.password),
            "WEBVAR_USERNAME": str(self.username)
        }

    def _parse_text(self, text):
        parser = slimit.parser.Parser()
        try:
            tree = parser.parse(text)
            fields = {getattr(x.left, 'value', ''): getattr(x.right, 'value', '')
                      for x in nodevisitor.visit(tree)
                      if isinstance(x, slimit.ast.Assign)}

            pat = re.compile(r'^[\'"]|[\'"]$')
            reqstrip = lambda x: re.sub(pat, '', x)

            try:
                parsed = {reqstrip(k): reqstrip(v) for (k, v) in fields.items()}
            except TypeError as err:
                print('{}'.format(err))
                sys.stderr.write('Couldn\'t parse text. Exiting...\n')
                sys.exit(10)

            return parsed
        except SyntaxError:
            print(text)
            sys.stderr("Couldn't parse text. Exiting...\n")
            sys.exit(10)


    def _connect(self):
        ipmi_host = self.dcim.get_ipmi_host()
        url = ipmi_host + self.URL_LOGIN

        cookies = self._get_console_cookies()
        headers = self._get_console_headers()
        data = self._get_console_data()

        self._session = requests.session()

        text = self._post(url, data, cookies, headers).text

        parsed = self._parse_text(text)
        session_token = parsed['SESSION_COOKIE']
        if session_token == 'Failure_Session_Creation':
            sys.stderr.write('Probably reached session limit')
            sys.exit(10)

        CSRF_token = parsed['CSRFTOKEN']

        self.session_token = {'SessionCookie': session_token}
        self.CSRF_token = {'CSRFTOKEN': CSRF_token}

    def _post(self, url, data, cookies, headers):
        return self._session.post(
            url,
            data=data,
            cookies=cookies,
            headers=headers,
            verify=False
        )

    def console(self):
        self._connect()

        ipmi_host = self.oob_info["ipmi"]
        url = ipmi_host + self.URL_VNC.format(ipmi_host.replace("https://", ""))
        answer = self._post(url, None, self.session_token,
            self.CSRF_token).text

        _, myjviewer = tempfile.mkstemp()
        m = '\n<argument>-title</argument>\n<argument>{}</argument>'
        m = m.format(self.oob_info["identifier"])
        to_repl = '<argument>35</argument>'
        answer = answer.replace(to_repl, to_repl+m)

        with open(myjviewer, 'w') as f:
            f.write(answer)

        try:
            Popen(['/usr/bin/javaws', myjviewer])
        except:
            sys.stderr.write("Couldn't open Java console. Exiting...\n")
            sys.exit(10)

