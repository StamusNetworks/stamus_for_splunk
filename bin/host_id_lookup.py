#!/usr/bin/env python

import csv
import sys
import os

from lib.stamus.common import StamusRestConnection


def hostid_lookup_hostname(hostname):
    snc = StamusRestConnection()
    HOST_URL = '/rest/appliances/host_id_alerts/?host_id_qfilter=' + hostname
    resp = snc.get(HOST_URL)
    data = resp.get('results', [])
    ips = []
    if data is None:
        return []
    for host in data:
        ips.append(host['ip'])
    return ips


def hostid_lookup_ip(ip):
    snc = StamusRestConnection()
    IP_URL = "/rest/appliances/host_id/" + ip
    resp = snc.get(IP_URL)
    data = resp.get('host_id', {}).get('hostname')
    hostnames = []
    if data is None:
        return [ip]
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

