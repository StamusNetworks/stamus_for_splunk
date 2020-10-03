#!/usr/bin/env python

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from lib.stamus.common import StamusRestConnection, StamusHostIdFilters

from splunklib.searchcommands import dispatch, EventingCommand, Configuration, Option
from splunklib.searchcommands.validators import Code

@Configuration()
class HostIdFilterCommand(EventingCommand):
    """ Filters, augments, and updates records on the events stream.
    ##Syntax
    .. code-block::
        snhostfilter filter=<expression>
    ##Description
    Filter events to get only events where or the source or the destination IP
    is in the host ID set defined by the filter.
    ##Example
    Display only alerts for IP that run a service on port 443.
    .. code-block::
        | even_type="alert"
        | hostiffilter filter="service.port=443"
    """
    filter = Option(doc='''
        **Syntax:** **filter=***<expression>*
        **Description:** Use space separated field=val filter.
        ''')
    keys = Option(doc='''
        **Syntax:** **keys=***<expression>*
        **Description:** Comma separated list of fields that are IPs.
        ''')


    HOST_URL = '/rest/appliances/host_id/'

    def __init__(self):
        super(HostIdFilterCommand, self).__init__()
        self.ips_list = None

    def transform(self, records):
        if not self.filter:
            for record in records:
                yield record
            return

        if not self.keys:
            self.keys = ['src_ip', 'dest_ip']
        else:
            self.keys = self.keys.split(',')

        if self.ips_list is None:
            snc = StamusRestConnection()
            # Do search
            filters = StamusHostIdFilters(self.filter).get()
            resp = snc.get(self.HOST_URL, params = filters)
            while resp is not None:
                data = resp.get('results', [])
                self.ips_list = [host['ip'] for host in data]
                resp = snc.get(self.HOST_URL, params = filters)

        for record in records:
            for key in self.keys:
                if record.get(key) in self.ips_list:
                    yield record
                    break
        return


dispatch(HostIdFilterCommand, sys.argv, sys.stdin, sys.stdout, __name__)
