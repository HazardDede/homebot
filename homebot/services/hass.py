"""Home assistant related services."""

import json
import re
from typing import Any, Optional, Dict, Iterable

import attr
from typeguard import typechecked

from homebot.validator import attrs_assert_type


@attr.s
class HassEntity:
    """Home assistant entity data container."""
    domain: str = attr.ib()
    entity_name: str = attr.ib()
    friendly_name: Optional[str] = attr.ib()
    device_class: Optional[str] = attr.ib()
    state: Any = attr.ib()
    unit_of_measurement: Optional[str] = attr.ib()

    @property
    def entity_id(self) -> str:
        """Return the entity id (domain.entity_name)."""
        return f"{self.domain}.{self.entity_name}"

    @classmethod
    def from_response(cls, response: Iterable[Dict[str, Any]]) -> Iterable['HassEntity']:
        """Parses the entity from ther response of a home assistant rest-api call."""
        def _single(payload: Dict[str, Any]) -> 'HassEntity':
            entity_id = payload['entity_id']
            domain, entity_name = entity_id.split('.', 1)
            return cls(
                domain=domain,
                entity_name=entity_name,
                friendly_name=payload.get('attributes', {}).get('friendly_name'),
                device_class=payload.get('attributes', {}).get('device_class'),
                state=payload['state'],
                unit_of_measurement=payload.get('attributes', {}).get('unit_of_measurement', '')
            )

        return [_single(item) for item in response]


@attr.s
class HassStateChange:
    """Home assistant state change data container."""
    friendly_name: str = attr.ib(validator=attrs_assert_type(str))
    entity_id: str = attr.ib(validator=attrs_assert_type(str))
    state: str = attr.ib(validator=attrs_assert_type(str))

    @classmethod
    def from_api_response(cls, resp: Any) -> Iterable['HassStateChange']:
        """Returns a list of `HassStateChanges` parsed from an home assistant api response."""
        return [
            cls(
                friendly_name=item.get('attributes', {}).get('friendly_name', ''),
                entity_id=item.get('entity_id', ''),
                state=item.get('state', 'unknown')
            )
            for item in resp
        ]


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

    @typechecked
    async def states(self, domain: Optional[str] = None, entity_pattern: Optional[str] = None) -> Iterable[HassEntity]:
        """Calls the endpoint /api/states to retrieve the current state of each entity."""
        def _entity_filter(entity: HassEntity) -> bool:
            return bool(regex.match(entity.entity_name)) or bool(regex.match(entity.friendly_name or ""))

        entities = HassEntity.from_response(await self.call(endpoint='states'))

        if domain:
            entities = [item for item in entities if item.domain.lower() == domain.lower()]

        if entity_pattern:
            regex = re.compile(entity_pattern, flags=re.IGNORECASE)
            entities = [item for item in entities if _entity_filter(item)]

        return entities

    @typechecked
    async def switch_on_off(self, domain: str, entity: str, turn_on: bool = True) -> Iterable[HassStateChange]:
        """Calls the service endpoint homeassistant/[turn_on|turn_off] to generically turn on/off the specified
        entity. The entity has to support it. Returns a list of state changes that occurred during the operation."""
        endpoint = 'services/homeassistant/' + ('turn_on' if turn_on else 'turn_off')

        data = {'entity_id': f'{domain}.{entity}'}
        res = await self.call(endpoint, method=HassApi.METHOD_POST, data=data)

        return HassStateChange.from_api_response(res)
