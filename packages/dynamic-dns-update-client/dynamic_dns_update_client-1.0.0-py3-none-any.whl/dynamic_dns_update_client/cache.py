"""Cache module."""

from pathlib import Path


def write_cached_ip_address(ip_address: str, cache_file: str) -> None:
    """Write IP address to a file.

    :param ip_address:
    :param cache_file:
    :return:
    """
    cache_file_path = Path(cache_file)
    with open(cache_file_path, "w") as file:
        file.write(ip_address)


def read_cached_ip_address(cache_file: str) -> str | None:
    """Read IP address from a file.

    :param cache_file:
    :return:
    """
    cache_file_path = Path(cache_file)
    if cache_file_path.exists():
        ip_address = cache_file_path.read_text()
        return ip_address.strip()
    else:
        return None
