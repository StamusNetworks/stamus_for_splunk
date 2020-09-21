#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

from lib.stamus.common import StamusRestConnection, StamusHostIdFilters


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
            host['host_id']['ip'] = host['ip']
            yield({'_raw': json.dumps(host['host_id'])})
        pass

dispatch(HostIDSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)

