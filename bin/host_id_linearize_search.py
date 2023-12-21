#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

from lib.stamus.common import StamusRestConnection, StamusHostIdFilters, FIELDS_SUBSTITUTION_DICT

from datetime import datetime, timezone

ARRAY_ITEMS = ['client_service', 'hostname', 'username', 'http.user_agent', 'tls.ja3', 'tls.ja4', 'ssh.client', 'roles']
ITEM_KEY = {'client_service': 'name', 'hostname': 'host', 'username': 'user', 'http.user_agent': 'agent', 'tls.ja3': 'hash', 'tls.ja4': 'hash', ssh.client': 'software_version', 'roles': 'name', 'services': 'app_proto'}

@Configuration(type='events')
class HostIDSearchLinearizeCommand(GeneratingCommand):
    """ %(synopsis)
    ##Syntax
    %(syntax)
    ##Description
    %(description)
    """
    filter = Option(require=False)

    def timestamp_to_unix(self, timestamp):
        utc_dt = datetime.fromisoformat(timestamp)
        return (utc_dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()

    def generate(self):
        HOST_URL = '/rest/appliances/host_id/'
        snc = StamusRestConnection(metadata=self.metadata)
        # Do search
        filters = None
        if self.filter:
            filters = StamusHostIdFilters(self.filter).get()
        resp = snc.get(HOST_URL, params = filters)
        while resp:
            data = resp.get('results', [])
            for host in data:
                host_data = host['host_id']
                item_data = {'ip': host['ip']}
                item_data['event_type'] = 'discovery'
                item_data['first_seen'] = host_data['first_seen']
                if 'last_seen' in host_data:
                    item_data['last_seen'] = host_data['last_seen']
                if 'net_info' in host_data:
                    item_data['net_info'] = host_data['net_info']
                host_services = host_data.get('services')
                if host_services is not None:
                    item_data['type'] = 'service'
                    for service in host_services:
                        for value in service['values']:
                            item_data['service'] = value
                            item_data['service']['proto'] = service['proto']
                            item_data['service']['port'] = service['port']
                            item_data['value'] = value['app_proto']
                            if '+' in value['first_seen'] and value['first_seen'][-3] != ':':
                                item_data['timestamp'] = value['first_seen'][:-2] + ':' + value['first_seen'][-2:]
                            else:
                                item_data['timestamp'] = value['first_seen']
                            timestamp = self.timestamp_to_unix(item_data['timestamp'])
                            yield({'_raw': json.dumps(item_data), '_time': timestamp})
                    item_data.pop('service')
                for key in ARRAY_ITEMS:
                    if key in host_data:
                        if key in FIELDS_SUBSTITUTION_DICT:
                            item_data['type'] = FIELDS_SUBSTITUTION_DICT[key]
                        else:
                            item_data['type'] = key
                        for item in host_data[key]:
                            if key in FIELDS_SUBSTITUTION_DICT:
                                item_data[FIELDS_SUBSTITUTION_DICT[key]] = item
                            else:
                                item_data[key] = item
                            item_data['value'] = item[ITEM_KEY[key]]
                            item_data['timestamp'] = item['first_seen']
                            timestamp = self.timestamp_to_unix(item_data['timestamp'])
                            yield({'_raw': json.dumps(item_data), '_time': timestamp})
                        item_data.pop('timestamp')
                        if key in FIELDS_SUBSTITUTION_DICT:
                            item_data.pop(FIELDS_SUBSTITUTION_DICT[key])
                        else:
                            item_data.pop(key)
            resp = snc.get(HOST_URL, params = filters)
        pass

dispatch(HostIDSearchLinearizeCommand, sys.argv, sys.stdin, sys.stdout, __name__)

