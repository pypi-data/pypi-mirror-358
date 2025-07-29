"""Utilities."""

from pathlib import Path
from subprocess import CompletedProcess, run

from requests.models import PreparedRequest


def execute_cli_command(arguments: str) -> str:
    """Execute a command.

    :param arguments:
    :return:
    """
    result: CompletedProcess = run(
        arguments, capture_output=True, text=True, check=True, shell=True
    )
    return result.stdout


def file_exists(path: str) -> bool:
    """Get IP address for a network.

    :param path:
    :return:
    """
    return Path(path).exists()


def create_url_parameter(
    ip_address_url_parameter_name: str,
    url_parameter: tuple[str, ...],
    current_ip_address: str,
) -> dict[str, str | list[str]]:
    """Create URL parameter.

    :param ip_address_url_parameter_name:
    :param url_parameter:
    :param current_ip_address:
    :return:
    """
    params: dict[str, str | list[str]] = {
        ip_address_url_parameter_name: current_ip_address
    }

    for data in url_parameter:
        parts = data.split("=")
        key = parts[0]
        value = parts[1]

        if key in params.keys():
            if isinstance(params[key], list):
                value_list: list[str] = params[key]
                value_list.append(value)
                params[key] = value_list
            else:
                params[key] = [params[key], value]
        else:
            params[key] = value

    return params


def generate_url(
    dynamic_dns_provider_url: str,
    ip_address_url_parameter_name: str,
    url_parameter: tuple[str, ...],
    current_ip_address: str,
) -> str:
    """Send IP address update to dynamic DNS provider.

    :param dynamic_dns_provider_url:
    :param ip_address_url_parameter_name:
    :param url_parameter:
    :param current_ip_address:
    :return:
    """
    params = create_url_parameter(
        ip_address_url_parameter_name, url_parameter, current_ip_address
    )

    # See: https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests
    prepared_request = PreparedRequest()
    prepared_request.prepare_url(dynamic_dns_provider_url, params)
    return prepared_request.url
