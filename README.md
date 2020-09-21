
## Installation

After installing the application you need to setup the connectivity with your Scirius Security Platform.

To do so create a file `local/ssp.conf` under the application directory (`/opt/splunk/etc/apps/stamus` usually)
and setup the following:

```
[config]
api_key = 7909d2b1557fd7a99b999360bc79ddb418f69e27
base_url = https://10.136.0.14
check_tls = no
```

## Usage

### Host ID search

To retrieve all Host ID entries

```
| hostidsearch
```

To select following a filter:

```
| hostidsearch filter="hostname.host=zopenret.top services.port=443"
```

Get a top of hostname (by count of IP) running a service on port 443 and in network `internet`:
```
| hostidsearch filter="services.port=443 net_info.agg=internet"| spath "hostname{}.host" | top "hostname{}.host"
```

Get software version of all HTTP server in a network:

```
| hostidsearch filter="services.port=80 net_info.agg=internet"| spath "services{}.values{}.http.server" | top "services{}.values{}.http.server"
```


### Host ID filter

Select only events where `src_ip` or `dest_ip` is in the host ID set defined by the filter.

The following search get all alerts for host running a service on port 443.

```
event_type="alert" | hostidfilter filter="services.port=443"
```

### Host ID lookup


The following search gets all Stamus event and resolve destination ip to hostname.

```
event_type="stamus"| lookup hostidlookup ip as dest_ip| stats count by hostname
```

List all Stamus offenders and resolve IP to name using host ID data:

```
event_type="stamus"| lookup hostidlookup ip as stamus.source| top stamus.source, hostname
```

Get all Stamus Threats, then resolve asset IP to name and display threat per asset statistics:

```
event_type="threat" | lookup hostidlookup ip as asset | stats min(timestamp), max(timestamp) by threat, asset, hostname
```


Display all Stamus Threats events and output a table where asset IP has been resolved to name:

```
event_type="stamus" | lookup hostidlookup ip as stamus.asset | stats min(timestamp) as start_seen, max(timestamp) as last_seen by stamus.threat_id, stamus.asset, stamus.asset_net_info, hostname
```

### Thread ID lookup


### MISC

```
event_type="stamus" | stats min(timestamp) as start_seen, max(timestamp) as last_seen by stamus.asset, stamus.threat_id | eval iso8601_start=strptime(start_seen,"%Y-%m-%dT%H:%M:%S.%6N%z") | eval iso8601_end=strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%6N%z") |  eval duration=1000*(iso8601_end-iso8601_start) | eval _time=start_seen | stats count by _time, duration, stamus.asset, stamus.threat_id | table _time, stamus.asset, stamus.threat_id, duration
```
