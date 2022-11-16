#!/usr/bin/env python
import requests
import re
import shlex

from splunk.clilib import cli_common as cli


FIELDS_SUBSTITUTION = (['http.user_agent', 'http_user_agent'], ['http.user_agent_count', 'http_user_agent_count'], ['tls.ja3', 'tls_ja3'], ['tls.ja3_count', 'tls_ja3_count'], ['ssh.client', 'ssh_client'], ['ssh.client_count', 'ssh_client_count'])

FIELDS_SUBSTITUTION_DICT = {'http.user_agent': 'http_user_agent', 'http.user_agent_count': 'http_user_agent_count', 'tls.ja3': 'tls_ja3', 'tls.ja3_count': 'tls_ja3_count', 'ssh.client': 'ssh_client', 'ssh.client_count': 'ssh_client_count'}

class StamusRestConnection(object):
    def __init__(self, metadata=None):
        cfg = cli.getConfStanza('ssp', 'config')
        self.api_key = cfg.get('api_key')
        self.base_url = cfg.get('base_url')
        check_tls = cfg.get('check_tls')
        if check_tls.lower() in ['no', 'false']:
            self.check_tls = False
        else:
            self.check_tls = True
        self.headers = { 'Content-Type': 'application/json', 'Authorization': 'Token ' + self.api_key }
        self.next = None
        self.page = 1
        if metadata is not None:
            try:
                self.start_date = int(metadata.searchinfo.earliest_time)
                self.end_date = int(metadata.searchinfo.latest_time)
            except:
                pass
        else:
            self.start_date = None
            self.end_date = None

    def get(self, url, params = None):
        if not self.next and self.page != 1:
            return None
        direct_url = self.base_url + url
        if params is None:
            params = {}
        params['page'] = self.page
        params['page_size'] = 1000
        if self.start_date:
            params['start_date'] = self.start_date
            params['end_date'] = self.end_date
        if direct_url.startswith("https"):
            resp = requests.get(direct_url, headers=self.headers, verify=self.check_tls, params=params)
        else:
            raise(Exception("non HTTPS url are not allowed"))
        if resp.status_code != 200:
            # This means something went wrong.
            raise(Exception('API error: response status %d from SCS' % (resp.status_code)))
        data = resp.json()
        self.next = data.get('next')
        self.page +=1
        return data


class StamusHostIdFilters(object):
    FILTER_PREFIX = 'host_id_qfilter'
    def __init__(self, filters):
        cfg = cli.getConfStanza('ssp', 'config')
        tenant = cfg.get('tenant')
        if tenant:
            self.tenant = int(tenant)
        else:
            self.tenant = None
        filters_list = shlex.split(filters)
        for filt in filters_list:
            for item in FIELDS_SUBSTITUTION:
                if filt.startswith(item[1] + '.') or filt.startswith(item[1] + '='):
                    frep = filt.replace('_','.',1)
                    filters_list.remove(filt)
                    filters_list.append(frep)
                    break
        prefixed_filters = []
        for filt in filters_list:
            if filt.startswith('ip'):
                prefixed_filters.append(filt)
            else:
                prefixed_filters.append('host_id.' + filt)
        self.filters = []
        for filt in prefixed_filters:
            if '=' not in filt and '>' not in filt and '<' not in filt:
                raise(Exception('Invalid filter: %s' % (filt)))
            if '!' in filt:
                if filt.index('!') + 1 == filt.index('='):
                    ress = 'NOT ' + filt.replace('!=', ':', 1)
                    self.filters.append(ress)
                    continue
            self.filters.append(filt.replace('=', ':', 1))

    def get(self):
        str_filters = ' AND '.join(self.filters)
        result = { self.FILTER_PREFIX: str_filters }
        if self.tenant:
            result['tenant'] = self.tenant
        return result
