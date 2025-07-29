"""Dynamic DNS provider update."""

from requests import Response, get
from requests.auth import HTTPBasicAuth

from dynamic_dns_update_client.utils import create_url_parameter


def update_dyn_dns_provider(
    dynamic_dns_provider_url: str,
    ip_address_url_parameter_name: str,
    url_parameter: tuple[str, ...] | None,
    basic_auth_username: str,
    basic_auth_password: str,
    current_ip_address: str,
) -> None:
    """Send IP address update to dynamic DNS provider.

    :param dynamic_dns_provider_url:
    :param ip_address_url_parameter_name:
    :param url_parameter:
    :param basic_auth_username:
    :param basic_auth_password:
    :param current_ip_address:
    :return:
    """
    params = create_url_parameter(
        ip_address_url_parameter_name, url_parameter, current_ip_address
    )

    if basic_auth_username and basic_auth_password:
        basic_auth: HTTPBasicAuth = HTTPBasicAuth(
            basic_auth_username, basic_auth_password
        )
        response: Response = get(
            dynamic_dns_provider_url, auth=basic_auth, params=params
        )
    else:
        response: Response = get(dynamic_dns_provider_url, params=params)
    response.raise_for_status()
