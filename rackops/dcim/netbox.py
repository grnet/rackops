import requests
import json
import sys
import os
import logging

from rackops.dcim.base import DcimBase, DcimError

class Netbox(DcimBase):
    def __init__(self, identifier, is_rack, is_rack_unit, is_serial, dcim_params):
        super(Netbox, self).__init__(identifier, is_rack, is_rack_unit, is_serial, dcim_params)
        self.info = self._retrieve_info()

    def _get_params(self):
        if self.is_serial:
            return {"serial": self.identifier}
        elif self.is_rack_unit:
            return {"name": self.identifier}
        elif self.is_rack:
            return {"rack_id": self._get_rack_id()}
        else:
            return {"q": self.identifier}

    def _get_rack_id(self):
        logging.info("Querying the Netbox API for rack {}".format(self.identifier))
        url = os.path.join(self.api_url, "api/dcim/racks/")
        params = {"name": self.identifier}
        json_response = self._do_request(url, params)

        logging.info("Decoding the response")
        # we expect the response to be a json object
        response = json_response.json()
        if len(response["results"]) != 1:
            raise DcimError("Didn't find valid results for rack {}".format(self.identifier))
        return response["results"][0]["id"]

    def _get_headers(self):
        headers = {"Accept": "application/json"}

        token = self.dcim_params.get("netbox_token")
        if token is not None:
            headers.update({"Authorization": f"Token: {token}"})
        return headers

    def _do_request(self, url, params):
        headers = self._get_headers()

        logging.debug("Will do a GET request on" \
            "url {} with params {} and headers {}".format(
                url, str(params), str(headers)
            ))
        try:
            return requests.get(url, params=params, headers=headers)
        except requests.exceptions.Timeout as e:
            # useful instead of a long exception dump
            sys.stderr.write(
                "Request timed out for **netbox** dcim %s. Exiting...\n" % url)
            exit(1)

    def _retrieve_info(self):
        logging.info("Querying the Netbox API for {}".format(self.identifier))
        url = os.path.join(self.api_url, "api/dcim/devices/")
        params = self._get_params()
        json_response = self._do_request(url, params)

        logging.info("Decoding the response")
        # we expect the response to be a json object
        return json_response.json()


    def get_short_info(self, result):
        return {
            "name": result["name"],
            "display_name": result["display_name"],
            "serial": result["serial"],
            "ipmi": result["custom_fields"]["IPMI"],
            "manufacturer": result["device_type"]["manufacturer"]["slug"]
        }

    def get_info(self):
        return self.info

    def get_oobs(self):
        for result in self.info["results"]:
            yield {
                "asset_tag": result["asset_tag"],
                "ipmi": result["custom_fields"]["IPMI"],
                "oob": result["device_type"]["manufacturer"]["slug"],
                "info": self.get_short_info(result),
                "identifier": result["name"]
            }
