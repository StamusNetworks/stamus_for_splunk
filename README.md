
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
