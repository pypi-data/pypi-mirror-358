"""Command line interface."""

# ruff: noqa: D301, D401

import click

from dynamic_dns_update_client.cache import (
    read_cached_ip_address,
    write_cached_ip_address,
)
from dynamic_dns_update_client.constants import CACHE_FILE
from dynamic_dns_update_client.dyn_dns_update import update_dyn_dns_provider
from dynamic_dns_update_client.ip_address import IpAddressProviderType, get_ip_address
from dynamic_dns_update_client.types import UrlParameterType, UrlType
from dynamic_dns_update_client.utils import generate_url


@click.command()
@click.argument(
    "dynamic_dns_provider_url",
    type=UrlType(),
    required=True,
)
@click.option(
    "--ip-address-provider",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_IP_ADDRESS_PROVIDER",
    type=click.Choice(IpAddressProviderType, case_sensitive=False),
    default=IpAddressProviderType.IPIFY,
    help=f"Type of IP address provider. Default: {IpAddressProviderType.IPIFY.value}",
)
@click.option(
    "--ipv6",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_IPV6",
    is_flag=True,
    help="Obtain IP V6 address from IP address provider.",
)
@click.option(
    "--openwrt-network",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_OPENWRT_NETWORK",
    default="wan",
    help="OpenWRT network to look for the public IP address. Default: wan",
)
@click.option(
    "--interface",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_INTERFACE",
    default="eth0",
    help="Physical interface to look for the public IP address. Default: eth0",
)
@click.option(
    "--ip-address-url-parameter-name",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_IP_ADDRESS_URL_PARAMETER_NAME",
    required=True,
    help="Name of the URL parameter for IP address. "
    "It will be appended to the dynamic DNS provider URL.",
)
@click.option(
    "--url-parameter",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_URL_PARAMETER",
    type=UrlParameterType(),
    multiple=True,
    help="URL parameter which will be appended to the dynamic DNS provider URL. "
    "You can specify this option multiple times. Format: param=value",
)
@click.option(
    "--basic-auth-username",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_BASIC_AUTH_USERNAME",
    help="Basic Auth username for calling dynamic DNS provider URL.",
)
@click.option(
    "--basic-auth-password",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_BASIC_AUTH_PASSWORD",
    help="Basic Auth password for calling dynamic DNS provider URL.",
)
@click.option(
    "--dry-run",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_DRY_RUN",
    is_flag=True,
    help="Instead of calling the dynamic DNS provider, "
    "print the URL which would have been called.",
)
@click.option(
    "--cache-ip-address",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_CACHE_IP_ADDRESS",
    is_flag=True,
    help="Cache the IP address.",
)
@click.option(
    "--cache-file",
    envvar="DYNAMIC_DNS_UPDATE_CLIENT_CACHE_FILE",
    default=CACHE_FILE,
    help=f"Cache file for the IP address. Default: {CACHE_FILE}",
)
def cli(
    dynamic_dns_provider_url: str,
    ip_address_provider: IpAddressProviderType,
    ipv6: bool,
    openwrt_network: str,
    interface: str,
    ip_address_url_parameter_name: str,
    url_parameter: tuple[str, ...] | None,
    basic_auth_username: str | None,
    basic_auth_password: str | None,
    dry_run: bool,
    cache_ip_address: bool,
    cache_file: str,
) -> None:
    """Dynamic DNS Update Client.

    A CLI tool for obtaining and updating your public IP address at dynamic DNS
    providers.

    It obtains the current IP address by different means depending on the
    --ip-address-provider option:

    - openwrt_network: on an OpenWRT device by calling OpenWRT specific functions,
      specify network with --ip-network

    - interface: physical network interface to look for the public IP address,
      specify interface with --ip-interface

    - by calling one of the following IP address services using an HTTP GET request:

        - ipify: https://www.ipify.org/

        - dyndns: https://help.dyn.com/remote-access-api/checkip-tool/

    It then updates the obtained IP address with another HTTP GET request at the dynamic
    DNS provider using the specified URL parameters and authentication method.

    \f

    :param dynamic_dns_provider_url:
    :param ip_address_provider:
    :param openwrt_network:
    :param interface:
    :param ipv6:
    :param ip_address_url_parameter_name:
    :param url_parameter:
    :param basic_auth_username:
    :param basic_auth_password:
    :param dry_run:
    :param cache_ip_address:
    :param cache_file:
    :return:
    """
    # Verify basic auth options
    if basic_auth_username and basic_auth_password is None:
        raise click.BadOptionUsage(
            "--basic-auth-password", "Please specify also a Basic Auth password."
        )
    if basic_auth_password and basic_auth_username is None:
        raise click.BadOptionUsage(
            "--basic-auth-username", "Please specify also a Basic Auth username."
        )

    # Obtain current IP address
    current_ip_address: str = get_ip_address(
        ip_address_provider, openwrt_network, interface, ipv6
    )
    click.echo(f"Current IP address: {current_ip_address}")

    # Obtain cached IP address and cache current IP address
    if cache_ip_address:
        cached_ip_address = read_cached_ip_address(cache_file)
        write_cached_ip_address(current_ip_address, cache_file)
        click.echo(f"Cached IP address: {current_ip_address}")
    else:
        cached_ip_address = None

    if dry_run:
        url = generate_url(
            dynamic_dns_provider_url,
            ip_address_url_parameter_name,
            url_parameter,
            current_ip_address,
        )
        click.echo("Dry run, no changes will be made.")
        click.echo(f"Dynamic DNS provider URL: {url}")
    else:
        if cached_ip_address and cached_ip_address == current_ip_address:
            click.echo(
                "Current IP address equals cached IP address, "
                "so no update will be made."
            )
        else:
            update_dyn_dns_provider(
                dynamic_dns_provider_url,
                ip_address_url_parameter_name,
                url_parameter,
                basic_auth_username,
                basic_auth_password,
                current_ip_address,
            )
            click.echo(
                "The IP address was successfully updated at the dynamic DNS provider."
            )
