# Welcome to Stamus Networks App for Splunk® documentation

# Overview

## Introduction

Stamus Networks App for Splunk® is an application designed for Suricata sensors users,
including SELKS users, and Stamus Security Platform users.


## Installation

You can use the regular Splunk App installation procedure to install Stamus Networks App for Splunk®.
You may have to install the [Timeline App](https://splunkbase.splunk.com/app/3120/) and
[URL Toolbox](https://splunkbase.splunk.com/app/2734) to display some of
the visualizations.

After installing the application, you can directly use it if you are a Suricata sensors user and
don't have a Stamus Security Platform (SSP).

##  Configuration

When setting up the Splunk log collection (via Splunk forwarder or Spluk itself), you have to set the
source type to `suricata`. A typical entry in `inputs.conf` will look like:

```
[monitor:/var/log/suricata/eve.json]
disabled = false
index = mycustomindex
sourcetype = suricata
```

Note: Stamus Security Platform users have to choose `Suricata` as source type.

If you are using a custom index to store events, you will need to define which index to use.
To do this in the web application, you can go to `Settings > Advanced search > Search macros`
then click on `stamus_index`. Then simply edit the value. For example with an index named
`mycustomindex`, set the `Definition` to `index=mycustomindex`.

You can also do it by creating a `local/macros.conf` file in the directory of the application.
For an index named `mycustomindex`, it should look like:

```
[stamus_index]
definition = index=mycustomindex
iseval=0
```

Stamus Security Platform users need to setup the connectivity with their Stamus Central Server (SCS).

To do so, you need to create a file `local/ssp.conf` under the application directory (`/opt/splunk/etc/apps/stamus_for_splunk` usually)
and setup the following:

```
[config]
api_key = SCS_TOKEN
base_url = https://SCS_ADDRESS
check_tls = no
```

The `SCS_TOKEN` can be generated from Stamus Central Server by going to `Account Settings` via the user icon on the top right
and selecting `Edit token`. Only read access is necessary so a user with low privilege can be used.

If you have a multi tenant instance of Stamus Security Platform, you need to select a tenant by adding the ``tenant`` stanza
in the configuration (using the numeric tenant ID).

## Usage

### Dashboards and Reports

Dashboards and reports containing Suricata in their name are designed for Suricata sensors and do not require a Stamus Security Platform.

The others dashboards require connectivity or data coming from a SSP installation.

### Using data from Host Identification module of SSP

#### Concept

Stamus Security Platform features a module named Host Insights that builds identity cards of IP addresses seen
in the network without storing all raw events. This provides a concise view of the major attributes that can be linked
to an IP address.

An host identification entry includes:
- List of hostnames associated with the IP
- List of usernames that connected to this IP
- List of network services
- List of HTTP user agents
- List of TLS agents (using JA3 technology)
- List of SSH agents
- List of application protocol used as agents
- List of Roles (Domain Controllers, DHCP Servers, Printers, ...)

All this information is associated with a first-seen and last-seen timestamp, so it is possible to know
precisely when a username or a HTTP user agent was first seen on a given IP address.

#### Host Insights search

The App adds a `snhostsearch` command that queries Stamus Security Platform REST API to fetch Host Insights entries
matching a filter. The following are examples of filters that may be applied to the Host Insights module:

To retrieve ALL Host Insights entries, simply enter:

```
| snhostsearch
```

To select using a filter:

```
| snhostsearch filter="hostname.host=zopenret.top services.port=443"
```

To retrieve the top hostname (by count of IP) running a service on port 443 and not in network `internet`:

```
| snhostsearch filter="services.port=443 net_info.agg!=internet"| spath "hostname{}.host" | top "hostname{}.host"
```

To get software version of all HTTP server in a network (here `internet`):

```
| snhostsearch filter="services.values.app_proto=http net_info.agg=internet"| spath "services{}.values{}.http.server" | top "services{}.values{}.http.server"
```

To get all requests to nginx server where client IP is running a service on port 9997:

```
| source="nginx.log" sourcetype="access_combined" | snhostfilter filter="services.port=9997" keys="clientip" | top clientip
```

### Host Insights service search

This command is used to search in the services found on the network by Host Insights. For example, to list
all the services that are TLS and that are not running on port 443, one can do:


```
search = | snservicesearch filter="services.values.app_proto=tls services.port!=443"
```

### Host Insights linear search


This command is used to display all host insights events for a filter. For example to get information
about discovery time of all metadata on one IP:

```
| snlinearsearch filter="ip=192.0.2.146" | table timestamp ip event_type type value
```

#### Host Insights filter

The `snhostfilter` commands allow you to select only events where `src_ip` or `dest_ip` is in the host ID set defined by the filter.

The following search returns all alerts for hosts running a service on port 443.

```
event_type="alert" | snhostfilter filter="services.port=443"
```

#### Host Insights lookup

The `snhostlookup` lookup resolves ip to hostname (and reverse) using the hostname information collected by SSP.

The following search returns all alert events and resolve destination ip to hostname.

```
event_type="alert"| lookup snhostlookup ip as dest_ip| stats count by hostname
```

List all Stamus offenders and resolve IP to name using host ID data:

```
event_type="stamus"| lookup snhostlookup ip as stamus.source| top stamus.source, hostname
```

Display all Stamus Threats events and output a table where asset IP has been resolved to name:

```
event_type="stamus" | lookup snhostlookup ip as stamus.asset | stats min(timestamp) as start_seen, max(timestamp) as last_seen by stamus.threat_id, stamus.asset, stamus.asset_net_info, hostname
```


### Host Insights service search

The `snservicesearch` command searches in the Host Insights database and returns the list of services for the hosts
that match the provided filters.

List all services for host that run HTTP services that are not bound to port 80:

```
| snservicesearch filter="services.values.app_proto=http services.port!=80" | spath | search service.app_proto="http" service.port!=80
```

### Signature information

Alert events are not containing the content of the signature that did trigger them and this can be a problem during analysis.
This Splunk App includes a lookup in Stamus Security Platform (or Scirius CE) that adds the content of the signature to
the event. Here is a query example:

```
event_type = "alert"
| lookup sn_signature_lookup sid as alert.signature_id
| spath input=sig_info
| table src_ip, dest_ip, signature.content, signature.imported_date
```

Note: the `metadata` keyword is substituted in the content with `sig_params` to workaround a [problem in Splunk](https://community.splunk.com/t5/Developing-for-Splunk-Enterprise/How-to-remove-fields-containing-metadata-keyword-that-get-html/m-p/592421).

# Release Note

## Release 1.0.4

- Splunk compatibiliy work

## Release 1.0.3

- Update splunklib
- Fix some validation warnings

## Release 1.0.2

- Improve alert orientation
- Add JA4 in dashboards
- Update splunklib

## Release 1.0.1

- Only allow https connection to SCS
- Drill down in TLS dashboard
- Fix alert event type

## Release 1.0.0

- Multi tenant support (Stamus users)
- Remove snhreatfilter command (Stamus users)
- Add snservicesearch command (Stamus users)
- New TLS dashboards including TLS cipher suite analysis
- Add snlinearsearch (Stamus users)
- Stamus IP timeline using Host Insigths and DoC (Stamus users)
- Alert tag filtering on Stamus IDS dashboard (Stamus users)
- Stamus Policy Violations dashboard (Stamus users)

## Release 0.9.19

- Fix export of application variables
- Better filtering on data for Splunk with multiple data sources
- New SSP and Scirius CE lookup to see signature content in Splunk

## Release 0.9.17

- Fix form declaration
- Fix export of macros that was missing
- Update following renaming of Stamus Networks product

## Release 0.9.16

- Add file information dashboard

## Release 0.9.8

- Add anomaly dashboards

## Release 0.9.7

- Add drilldown to dashboards
- Minor fixes

## Release 0.9.6

- Splunk 7.x compatibility

## Version 0.9.5

- Better navigation
- Update colors
- Fix admin dashboard for multiple probes

## Version 0.9.3

- CIM 4.x compatibility
- keys option added to snhostfilter for easy cross source filtering
- rename all commands with a sn prefix for better completion
- performance optimizations of dashboards

## Version 0.9.2

- Improve IDS dashboards
- Fix timestamp picker in Suricata admin Dashboard

## Version 0.9.1

Fix errors and warnings found by Splunk AppInspect

## Version 0.9.0

Initial release.

Features:

- dashboards for Suricata and Stamus Security Platform from Stamus Networks
- snhostsearch: search host identification entries in Stamus Security Platform 
- snhostfilter: filter query on host matching a request done in host identification entries
- snthreatfilter: resolves Stamus threat id to Stamus threat name
- snhostlookup: do ip to hostname resolution and reverse using host identification data

