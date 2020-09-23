#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

from lib.stamus.common import StamusRestConnection, StamusHostIdFilters, FIELDS_SUBSTITUTION


@Configuration(type='events')
class HostIDSearchCommand(GeneratingCommand):
    """ %(synopsis)
    ##Syntax
    %(syntax)
    ##Description
    %(description)
    """
    filter = Option(require=False)

    def generate(self):
        HOST_URL = '/rest/appliances/host_id_alerts/'
        snc = StamusRestConnection()
        # Do search
        filters = None
        if self.filter:
            filters = StamusHostIdFilters(self.filter).get()
        resp = snc.get(HOST_URL, params = filters)
        data = resp.get('results', [])
        for host in data:
            host_data = host['host_id']
            host_data['ip'] = host['ip']
            for field in FIELDS_SUBSTITUTION:
                if host_data.get(field[0]):
                    host_data[field[1]] = host_data.pop(field[0])
            yield({'_raw': json.dumps(host_data)})
        pass

dispatch(HostIDSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)

