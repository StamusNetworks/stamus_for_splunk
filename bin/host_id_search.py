#!/usr/bin/env python

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators

from stamus import StamusRestConnection

HOST_URL = '/rest/appliances/host_id_alerts/'

@Configuration(type='events')
class HostIDSearchCommand(GeneratingCommand):
    """ %(synopsis)
    ##Syntax
    %(syntax)
    ##Description
    %(description)
    """
    
    def generate(self):
        snc = StamusRestConnection()
        # Do search
        resp = snc.get(HOST_URL)
        data = resp.get('results', [])
        for host in data:
            host['host_id']['ip'] = host['ip']
            yield(host['host_id'])       
        pass

dispatch(HostIDSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)

