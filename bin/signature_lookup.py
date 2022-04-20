#!/usr/bin/env python3
import csv
import sys
import json

from lib.stamus.common import StamusRestConnection

"""
curl -s -k -X GET https://<SSP_SERVER>/rest/rules/rule/<SIGNATURE_ID>/ -H 'Authorization: Token <TOKEN>' -H 'Content-Type: application/json' | jq

{
  "pk": 2035184,
  "sid": 2035184,
  "category": {
    "pk": 46,
    "name": "malware",
    "descr": "",
    "created_date": "2021-05-05T15:37:48.444568+02:00",
    "source": 1
  },
  "msg": "ET MALWARE Go/Anubis Registration Activity",
  "state": true,
  "state_in_source": true,
  "rev": 2,
  "content": "alert tcp $HOME_NET any -> $EXTERNAL_NET any (msg:\"ET MALWARE Go/Anubis Registration Activity\"; dsize:<400; content:\"|54 67 69 2f 40|\"; within:50; content:\"|4f 6b 65 74 71 75 71 68 76 22 59 6b 70 66 71 79 75 22 5d 58 67 74 75 6b 71 70|\"; fast_pattern; reference:md5,1f21b8e9ebc3b7480cc67ced7504916f; reference:url,medium.com/walmartglobaltech/privateloader-to-anubis-loader-55d066a2653e; classtype:trojan-activity; sid:2035184; rev:2; metadata:attack_target Client_Endpoint, created_at 2022_02_14, deployment Perimeter, former_category MALWARE, signature_severity Major, updated_at 2022_02_14;)\n",
  "imported_date": "2022-02-15T14:54:05.124259+01:00",
  "updated_date": "2022-02-15T14:54:05.124259+01:00",
  "created": "2022-02-14",
  "updated": "2022-02-14",
  "hits": 0
}


Command line debug/development:

# cat test.csv 
sid,sig_info

2035184,
#
# /opt/splunk/bin/splunk cmd python signature_lookup.py sid < test.csv 
"""

def _lookup_ssp_signature(sid):

    try:
        snc = StamusRestConnection()
    except Exception as e:
        sys.exit(-1)
    
    try:
        endpoint_path = "/rest/rules/rule/" + sid + '/'
        resp = snc.get(endpoint_path)
    except Exception as e:
        resp = {}

    # packaged into a field 'signature' so that we will have a nice 'signature.<something>' field
    # in Splunk after using Splunk's command spath to parse it.
    return {'signature': resp}
    

def main():
    if len(sys.argv) != 2:
        print("Usage: python signature_lookup.py [signature id]")
        sys.exit(1)

    sigfield = sys.argv[1]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)
    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:
        try:
            sigid = result[sigfield] # ex: sigid = 2034127
            data = _lookup_ssp_signature(sigid)
            result['sig_info'] = json.dumps(data)
        except Exception as e:
            pass
        
        w.writerow(result)

main()

