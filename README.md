
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

To retrieve all Host ID entries

```
| hostidsearch
```

To select following a filter:

```
| hostidsearch filter="hostname.host=zopenret.top services.port=443"
```

