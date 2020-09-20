#!/usr/bin/env python
import requests

from splunk.clilib import cli_common as cli


class StamusRestConnection(object):
    def __init__(self):
        cfg = cli.getConfStanza('ssp', 'config')
        self.api_key = cfg.get('api_key')
        self.base_url = cfg.get('base_url')
        check_tls = cfg.get('check_tls')
        if check_tls.lower() in ['no', 'false']:
            self.check_tls = False
        else:
            self.check_tls = True
        self.headers = { 'Content-Type': 'application/json', 'Authorization': 'Token ' + self.api_key }

    def get(self, url):
        direct_url = self.base_url + url
        resp = requests.get(direct_url, headers=self.headers, verify=self.check_tls)
        if resp.status_code != 200:
            # This means something went wrong.
            raise(Exception('API error'))
        return resp.json()
