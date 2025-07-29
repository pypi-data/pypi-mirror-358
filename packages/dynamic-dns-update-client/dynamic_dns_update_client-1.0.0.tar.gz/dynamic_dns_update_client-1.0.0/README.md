[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/max-pfeiffer/dynamic-dns-update-client/graph/badge.svg?token=lPYop1verl)](https://codecov.io/gh/max-pfeiffer/dynamic-dns-update-client)
[![Pipeline](https://github.com/max-pfeiffer/dynamic-dns-update-client/actions/workflows/pipeline.yml/badge.svg)](https://github.com/max-pfeiffer/dynamic-dns-update-client/actions/workflows/pipeline.yml)
![PyPI - Version](https://img.shields.io/pypi/v/dynamic-dns-update-client)

# Dynamic DNS Update Client
A CLI tool for obtaining and updating your public IP address at dynamic DNS providers.

Instead of supporting any dynamic DNS provider in the world (like almost any other tool I found), this CLI tool aims to
be a flexible tool kit. Using it, you can put together a solution which works for 90% of the use cases.

It obtains the current IP address by different means depending on the `--ip-address-provider` option:
* `openwrt_network` on an [OpenWRT](https://openwrt.org/) device by calling OpenWRT specific functions, specify network with `--ip-network`
* `interface` physical network interface to look for the public IP address, specify interface with `--ip-interface`
* by calling one of the following IP address services using an HTTP GET request:
  * [`ipify`](https://www.ipify.org/)
  * [`dyndns`](https://help.dyn.com/remote-access-api/checkip-tool/)

It then updates the obtained IP address with another HTTP GET request at the dynamic DNS provider using
the specified URL parameters and authentication method.

You can run it from any machine that has a Python v3 environment available. This also includes [OpenWRT](https://openwrt.org/)
routers where you can install a Python interpreter and this package (see instructions below).

This CLI tool plays together nicely with my other project [simple-dynamic-dns-aws](https://github.com/max-pfeiffer/simple-dynamic-dns-aws).
If you happen to have an AWS account, you can put together your own Dyn DNS server almost for free.

## Install
### Anywhere
```shell
$ pip install dynamic-dns-update-client 
```

### OpenWRT
For installing and running `dynamic-dns-update-client` on your [OpenWRT](https://openwrt.org/) router, you need to
install the [Python v3 interpreter](https://openwrt.org/docs/guide-user/services/python) and pip.
You need the packages `python3-light` and `python3-pip`. These can be installed via Luci web interface or via SSH:
```shell
$ opkg install python3-light python3-pip
```
You can install `dynamic-dns-update-client` using pip now:
```shell
$ pip install dynamic-dns-update-client
```

## Usage
```shell
$ dynamic-dns-update-client --help
Usage: dynamic-dns-update-client [OPTIONS] DYNAMIC_DNS_PROVIDER_URL

  Dynamic DNS Update Client.

  A CLI tool for obtaining and updating your public IP address at dynamic DNS
  providers.

  It obtains the current IP address by different means depending on the --ip-
  address-provider option:

  - openwrt_network: on an OpenWRT device by calling OpenWRT specific
  functions,   specify network with --ip-network

  - interface: physical network interface to look for the public IP address,
  specify interface with --ip-interface

  - by calling one of the following IP address services using an HTTP GET
  request:

      - ipify: https://www.ipify.org/

      - dyndns: https://help.dyn.com/remote-access-api/checkip-tool/

  It then updates the obtained IP address with another HTTP GET request at the
  dynamic DNS provider using the specified URL parameters and authentication
  method.

Options:
  --ip-address-provider [openwrt_network|interface|ipify|dyndns]
                                  Type of IP address provider. Default: ipify
  --ipv6                          Obtain IP V6 address from IP address
                                  provider.
  --openwrt-network TEXT          OpenWRT network to look for the public IP
                                  address. Default: wan
  --interface TEXT                Physical interface to look for the public IP
                                  address. Default: eth0
  --ip-address-url-parameter-name TEXT
                                  Name of the URL parameter for IP address. It
                                  will be appended to the dynamic DNS provider
                                  URL.  [required]
  --url-parameter URL_PARAMETER   URL parameter which will be appended to the
                                  dynamic DNS provider URL. You can specify
                                  this option multiple times. Format:
                                  param=value
  --basic-auth-username TEXT      Basic Auth username for calling dynamic DNS
                                  provider URL.
  --basic-auth-password TEXT      Basic Auth password for calling dynamic DNS
                                  provider URL.
  --dry-run                       Instead of calling the dynamic DNS provider,
                                  print the URL which would have been called.
  --cache-ip-address              Cache the IP address.
  --cache-file TEXT               Cache file for the IP address. Default:
                                  /tmp/dynamic_dns_update_client_cache
  --help                          Show this message and exit.
```

### Example
Use the `--dry-run` option to check if your CLI call is correct:
```shell
$ dynamic-dns-update-client https://example.com --ip-address-url-parameter-name ip-address --url-parameter domain=example.com --url-parameter api-token=nd4u33huruffbn --dry-run
Current IP address: 82.4.110.122
Dry run, no changes will be made.
Dynamic DNS provider URL: https://example.com/?ip-address=82.4.110.122&domain=example.com&api-token=nd4u33huruffbn
```
`dynamic-dns-update-client` will call that URL effectively when you scratch that `--dry-run` option after your test.

## Environment Variables
If you are concerned about security and don't want to use the CLI options for secrets or passwords, you can also use
the following environment variables to provide these values to Dynamic DNS Update Client.
```shell
DYNAMIC_DNS_UPDATE_CLIENT_IP_ADDRESS_PROVIDER=ipify
DYNAMIC_DNS_UPDATE_CLIENT_IPV6=0
DYNAMIC_DNS_UPDATE_CLIENT_IP_NETWORK=wan
DYNAMIC_DNS_UPDATE_CLIENT_IP_INTERFACE=eth0
DYNAMIC_DNS_UPDATE_CLIENT_IP_ADDRESS_URL_PARAMETER_NAME=ip
DYNAMIC_DNS_UPDATE_CLIENT_URL_PARAMETER="foo=bar boom=bang cat=mouse"
DYNAMIC_DNS_UPDATE_CLIENT_BASIC_AUTH_USERNAME=username
DYNAMIC_DNS_UPDATE_CLIENT_BASIC_AUTH_PASSWORD=password
DYNAMIC_DNS_UPDATE_CLIENT_DRY_RUN=0
DYNAMIC_DNS_UPDATE_CLIENT_CACHE_IP_ADDRESS=1
DYNAMIC_DNS_UPDATE_CLIENT_CACHE_FILE=/tmp/custom_cache_file
```

## Known issues
For obtaining the IP address with `--ip-address-provider interface` the [`ifcfg`](https://github.com/ftao/python-ifcfg)
library is used. [On OpenWRT this library errors out.](https://github.com/ftao/python-ifcfg/issues/76)
Please use `--ip-address-provider openwrt_network` on your [OpenWRT](https://openwrt.org/) router until
this is fixed.