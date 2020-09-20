#!/usr/bin/env python

import requests
import csv
import sys

APIKey = '7909d2b1557fd7a99b999360bc79ddb418f69e27'
BASE_URL = 'https://10.136.0.14'
CHECK_TLS = False

headers = { 'Content-Type': 'application/json', 'Authorization': 'Token ' + APIKey }

def hostid_lookup_hostname(hostname):
    HOST_URL = '/rest/appliances/host_id_alerts/?host_id_qfilter=' + hostname
    DIRECT_URL = BASE_URL + HOST_URL
    resp = requests.get(DIRECT_URL, headers=headers, verify=CHECK_TLS)
    if resp.status_code != 200:
        # This means something went wrong.
        print('not godo')
    data = resp.json().get('results', [])
    ips = []
    for host in data:
        ips.append(host['ip'])
    return ips


def hostid_lookup_ip(ip):
    IP_URL = "/rest/appliances/host_id/" + ip
    DIRECT_URL = BASE_URL + IP_URL
    resp = requests.get(DIRECT_URL, headers=headers, verify=CHECK_TLS)
    if resp.status_code != 200:
        # This means something went wrong.
        print('not good')
    data = resp.json().get('host_id', {}).get('hostname')
    hostnames = []
    for host in data:
        hostnames.append(host['host'])
    return hostnames

def main():
    if len(sys.argv) != 3:
        print("Usage: python host_id_lookup.py [host field] [ip field]")
        sys.exit(1)

    hostfield = sys.argv[1]
    ipfield = sys.argv[2]

    infile = sys.stdin
    outfile = sys.stdout

    r = csv.DictReader(infile)

    w = csv.DictWriter(outfile, fieldnames=r.fieldnames)
    w.writeheader()

    for result in r:
        # Perform the lookup or reverse lookup if necessary
        if result[hostfield] and result[ipfield]:
            # both fields were provided, just pass it along
            w.writerow(result)

        elif result[hostfield]:
            # only host was provided, add ip
            ips = hostid_lookup_hostname(result[hostfield])
            for ip in ips:
                result[ipfield] = ip
                w.writerow(result)

        elif result[ipfield]:
            # only ip was provided, add host
            hosts = hostid_lookup_ip(result[ipfield])
            for host in hosts:
                result[hostfield] = host
                w.writerow(result)

main()

