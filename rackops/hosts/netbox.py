import requests
import json
import sys

from rackops.hosts.base import HostBase

class Netbox(HostBase):
    def __init__(self, identifier, api_url):
        super(Netbox, self).__init__(identifier, api_url)
        self.info = self._retrieve_info()

    def _get_params(self):
        return {"q": self.identifier}

    def _get_headers(self):
        return {"Accept": "application/json"}

    def _do_request(self):
        url = self.api_url
        params = self._get_params()
        headers = self._get_headers()

        try:
            return requests.get(url, params=params, headers=headers)
        except requests.exceptions.Timeout as e:
            # useful instead of a long exception dump
            sys.stderr.write(
                "Request timed out for **netbox** host %s. Exiting...\n" % url)
            exit(1)

    def _retrieve_info(self):
        json_response = self._do_request()

        # we expect the response to be a json object
        return json_response.json()


    def get_short_info(self):
        result = self.info["results"][0]
        return {
            "name": result["name"],
            "display_name": result["display_name"],
            "serial": result["serial"],
            "ipmi": result["custom_fields"]["IPMI"],
            "manufacturer": result["device_type"]["manufacturer"]["slug"]
        }

    def get_info(self):
        return self.info

    def get_provider(self):
        return self.info["results"][0]["device_type"]["manufacturer"]["slug"]

    def get_ipmi_host(self):
        return self.info["results"][0]["custom_fields"]["IPMI"]
