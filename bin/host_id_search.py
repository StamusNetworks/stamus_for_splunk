#!/usr/bin/env python

import requests
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators
from splunk.clilib import cli_common as cli

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
        cfg = cli.getConfStanza('ssp', 'config')
        api_key = cfg.get('api_key')
        base_url = cfg.get('base_url')
        check_tls = cfg.get('check_tls')
        if check_tls.lower() in ['no', 'false']:
            check_tls = False
        else:
            check_tls = True
        # Do search
        direct_url = base_url + HOST_URL
        headers = { 'Content-Type': 'application/json', 'Authorization': 'Token ' + api_key }
        resp = requests.get(direct_url, headers=headers, verify=check_tls)
        if resp.status_code != 200:
            # This means something went wrong.
            print('not good')
        data = resp.json().get('results', [])
        for host in data:
            host['host_id']['ip'] = host['ip']
            yield(host['host_id'])       
        pass

dispatch(HostIDSearchCommand, sys.argv, sys.stdin, sys.stdout, __name__)

