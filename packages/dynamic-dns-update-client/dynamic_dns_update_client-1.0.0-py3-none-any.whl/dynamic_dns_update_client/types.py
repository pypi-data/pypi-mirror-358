"""Custom click types."""

from typing import Any
from urllib.parse import urlparse

import click


class UrlType(click.ParamType):
    """Custom click type for URL."""

    name = "url"

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> Any:
        """Validate and convert the value.

        :param value:
        :param param:
        :param ctx:
        :return:
        """
        if not isinstance(value, str):
            self.fail("URL needs to be of string type")
        try:
            result = urlparse(value)
            if all([result.scheme, result.netloc]):
                return value
            else:
                self.fail(f"No valid URL: {value}")
        except AttributeError:
            self.fail(f"No valid URL: {value}")


class UrlParameterType(click.ParamType):
    """Custom click type for URL."""

    name = "url_parameter"

    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> Any:
        """Validate and convert the value.

        :param value:
        :param param:
        :param ctx:
        :return:
        """
        valid = True

        if not isinstance(value, str):
            valid = False
        if "=" not in value:
            valid = False

        parts: list[str] = value.split("=")

        if len(parts) > 2:
            valid = False
        if len(parts) == 2 and (len(parts[0]) == 0 or len(parts[1]) == 0):
            valid = False

        if valid:
            return value
        else:
            self.fail(f"Invalid URL parameter: {value}")
