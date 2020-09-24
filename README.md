# Welcome to Stamus Networks App for Splunk® documentation

# Overview

## Introduction

Stamus Networks App for Splunk® is an application designed for Suricata sensors users
and Scirius Security Platform users.


## Installation

After installing the application, you can directly use it if you are Suricata sensors and
don't have a Scirius Security Platform (SSP).

Scirius Security Platform users need to setup the connectivity with their SSP.

To do so, you need to create a file `local/ssp.conf` under the application directory (`/opt/splunk/etc/apps/stamus_for_splunk` usually)
and setup the following:

```
[config]
api_key = YOURAPIKEY
base_url = https://SSP_ADDRESS
check_tls = no
```

## Usage

### Dashboards and Reports

Dashboards and reports containing Suricata in their name are designed for Suricata sensors and do not require a Scirius Security Platform.

The others ones require connectivity or data coming from a SSP.

### Using data from Host Identification module of SSP

#### Concept

Scirius Security Platform features a Host Identification module that builds identity cards of IP addresses seen
in the network without storing all raw events. This provide a concise view of the major features that can be linked
to an IP addresses.

An host identification entry includes:
- List of hostnames associated to the IP
- List of usernames that did connect to this IP
- List of network services
- List of HTTP user agents
- List of TLS agents (using JA3 technology)
- List of SSH agents

All these information are associated with a first seen and last seen timestamp, so it is possible to know
what when a username or a HTTP user agent has been seen for the first time on an IP address.

#### Host ID search

The App adds a `hostidsearch` command that queries Scirius Security Platform REST API to fetch Host ID entries
matching a filter.

To retrieve all Host ID entries, simply do:

```
| hostidsearch
```

To select following a filter:

```
| hostidsearch filter="hostname.host=zopenret.top services.port=443"
```

To get a top of hostname (by count of IP) running a service on port 443 and not in network `internet`:

```
| hostidsearch filter="services.port=443 net_info.agg!=internet"| spath "hostname{}.host" | top "hostname{}.host"
```

To get software version of all HTTP server in a network (here `internet`):

```
| hostidsearch filter="services.values.app_proto=http net_info.agg=internet"| spath "services{}.values{}.http.server" | top "services{}.values{}.http.server"
```

To get all hosts that are not running a version curl:

```
| hostidsearch filter="http_user_agent.agent!=curl*" | spath http_user_agent{}.agent output=agent | spath ip | top ip, agent
```

#### Host ID filter

The `hostidfilter` commands allow you to select only events where `src_ip` or `dest_ip` is in the host ID set defined by the filter.

The following search get all alerts for host running a service on port 443.

```
event_type="alert" | hostidfilter filter="services.port=443"
```

#### Host ID lookup

The `hostidlookup` lookup does resolution of ip to hostname (and reverse) using the hostname information collected by SSP.

The following search gets all alert events and resolve destination ip to hostname.

```
event_type="alert"| lookup hostidlookup ip as dest_ip| stats count by hostname
```

List all Stamus offenders and resolve IP to name using host ID data:

```
event_type="stamus"| lookup hostidlookup ip as stamus.source| top stamus.source, hostname
```

Display all Stamus Threats events and output a table where asset IP has been resolved to name:

```
event_type="stamus" | lookup hostidlookup ip as stamus.asset | stats min(timestamp) as start_seen, max(timestamp) as last_seen by stamus.threat_id, stamus.asset, stamus.asset_net_info, hostname
```

### Using data from Stamus Threat events

#### Concept

The Scirius Threat Radar inside SSP generates event with type `stamus` that are high fidelity events
generated from signatures or custom algorithms.

#### Thread ID lookup


Get threat by network and use `stamusthreatfilter` to do `threat_id` resolution:

```
event_type="stamus" | eval Network = if('stamus.asset_net_info' == "", "Unknown", 'stamus.asset_net_info') | stamusthreatfilter | stats dc(stamus.asset) as Assets by Network, threat_name
```

# Release Note

## Version 0.1.1

Initial release.

Features:

- dashboards for Suricata and Scirius Security Platform from Stamus Networks
- hostidsearch: search host identification entries in Scirius Security Platform 
- hostidfilter: filter query on host matching a request done in host identification entries
- stamusthreatfilter: resolve Stamus threat id to Stamus threat name
- hostidlookup: do ip to hostname resolution and reverse using host identification data

