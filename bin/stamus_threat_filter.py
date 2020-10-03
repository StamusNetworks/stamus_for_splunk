#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))

from lib.stamus.common import StamusRestConnection

from splunklib.searchcommands import dispatch, EventingCommand, Configuration, Option
from splunklib.searchcommands.validators import Code

@Configuration()
class StamusThreatFilterCommand(EventingCommand):
    """ Filters, augments, and updates records on the events stream.
    ##Syntax
    .. code-block::
        snthreatfilter
    ##Description
    Enrich Stamus threat event with information
    ##Example
    Display only alerts for IP that run a service on port 443.
    .. code-block::
        | even_type="stamus"
        | snthreatfilter
        | top stamus.threat_name
    """
    filter = Option(doc='''
        **Syntax:** **filter=***<expression>*
        **Description:** Use space separated field=val filter.
        ''')

    THREAT_URL = '/rest/appliances/threat/'

    def __init__(self):
        super(StamusThreatFilterCommand, self).__init__()
        self.threats_map = {}

    def resolve_threat_id(self, id):
        if self.threats_map.get(id):
            return self.threats_map[id]['name']

        snc = StamusRestConnection()
        resp = snc.get(self.THREAT_URL + str(id))
        self.threats_map[id] = resp
        return resp['name']

    def transform(self, records):
        for record in records:
            if record.get('event_type') == 'stamus':
                threat_id = json.loads(record['_raw'])['stamus']['threat_id']
                if threat_id:
                    record['threat_name'] = self.resolve_threat_id(threat_id)
            yield record
        return


dispatch(StamusThreatFilterCommand, sys.argv, sys.stdin, sys.stdout, __name__)
