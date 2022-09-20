#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

from lib.stamus.common import StamusRestConnection, StamusHostIdFilters, FIELDS_SUBSTITUTION


@Configuration(type='events')
class HostIDSearchServiceCommand(GeneratingCommand):
    """ %(synopsis)
    ##Syntax
    %(syntax)
    ##Description
    %(description)
    """
    filter = Option(require=False)

    def generate(self):
        HOST_URL = '/rest/appliances/host_id/'
        snc = StamusRestConnection()
        # Do search
        filters = None
        if self.filter:
            filters = StamusHostIdFilters(self.filter).get()
        resp = snc.get(HOST_URL, params = filters)
        while resp:
            data = resp.get('results', [])
            for host in data:
                host_data = host['host_id']
                service_data = {'ip': host['ip']}
                service_data['first_seen'] = host_data['first_seen']
                if 'last_seen' in host_data:
                    service_data['last_seen'] = host_data['last_seen']
                if 'net_info' in host_data:
                    service_data['net_info'] = host_data['net_info']
                for field in FIELDS_SUBSTITUTION:
                    if host_data.get(field[0]):
                        host_data[field[1]] = host_data.pop(field[0])
                host_services = host_data.get('services', [])
                for service in host_services:
                    for value in service['values']:
                        service_data['service'] = value
                        service_data['service']['proto'] = service['proto']
                        service_data['service']['port'] = service['port']
                        yield({'_raw': json.dumps(service_data)})
            resp = snc.get(HOST_URL, params = filters)
        pass

dispatch(HostIDSearchServiceCommand, sys.argv, sys.stdin, sys.stdout, __name__)

