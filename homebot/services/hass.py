"""Home assistant related services."""

import json
from typing import Any

import attr
from typeguard import typechecked


@attr.s
class HassApi:
    """Utility class to communicate with home assistant via the rest-api."""

    METHOD_GET = 'get'
    METHOD_POST = 'post'
    ALLOWED_METHODS = [METHOD_GET, METHOD_POST]

    DEFAULT_TIMEOUT = 5.0

    base_url: str = attr.ib(converter=str)
    token: str = attr.ib(converter=str)
    timeout: float = attr.ib(converter=float, default=DEFAULT_TIMEOUT)

    @typechecked
    async def call(self, endpoint: str, method: str = METHOD_GET, data: Any = None) -> Any:
        """Calls the specified endpoint (without prefix api) using the given method.
        You can optionally pass data to the request which will be json encoded."""
        from httpx import get, post
        import urllib.parse as urlparse

        method = str(method).lower()
        if method not in self.ALLOWED_METHODS:
            raise ValueError(
                "Argument method is expected to be one of {allowed}, but is '{method}'".format(
                    allowed=str(self.ALLOWED_METHODS),
                    method=method
                )
            )

        url = urlparse.urljoin(urlparse.urljoin(self.base_url, 'api/'), endpoint)
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-type': 'application/json',
        }

        if data is not None:
            data = json.dumps(data)

        if method == self.METHOD_GET:
            response = await get(url, headers=headers, timeout=self.timeout)
        else:
            response = await post(url, headers=headers, timeout=self.timeout, data=data)

        if response.status_code != 200:
            raise RuntimeError("Failed to call endpoint {url}"
                               "\nHttp Code: {response.status_code}"
                               "\nMessage: {response.text}".format(**locals()))

        return response.json()
