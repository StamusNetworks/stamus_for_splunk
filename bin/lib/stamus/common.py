#!/usr/bin/env python
import requests
import re

from splunk.clilib import cli_common as cli


FIELDS_SUBSTITUTION = (['http.user_agent', 'http_user_agent'], ['http.user_agent_count', 'http_user_agent_count'], ['tls.ja3', 'tls_ja3'], ['tls.ja3_count', 'tls_ja3_count'])

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

    def get(self, url, params = None):
        direct_url = self.base_url + url
        resp = requests.get(direct_url, headers=self.headers, verify=self.check_tls, params=params)
        if resp.status_code != 200:
            # This means something went wrong.
            raise(Exception('API error'))
        return resp.json()


class StamusHostIdFilters(object):
    FILTER_PREFIX = 'host_id_qfilter'
    def __init__(self, filters):
        filters_list = re.split(' +', filters)
        for filt in filters_list:
            for item in FIELDS_SUBSTITUTION:
                if filt.startswith(item[1] + '.') or filt.startswith(item[1] + '='):
                    frep = filt.replace('_','.',1)
                    filters_list.remove(filt)
                    filters_list.append(frep)
                    break
        self.filters = [x.replace('=', ':', 1) for x in filters_list]

    def get(self):
        prefixed_filters = []
        for filt in self.filters:
            if filt.startswith('ip:'):
                prefixed_filters.append(filt)
            else:
                prefixed_filters.append('host_id.' + filt)

        str_filters = ' AND '.join(prefixed_filters)
        return { self.FILTER_PREFIX: str_filters }
