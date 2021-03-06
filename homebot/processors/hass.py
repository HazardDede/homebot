"""Home assistant related processors."""
from typing import Any, Iterable, Optional

import attr

from homebot.models import HelpEntry, MessageIncoming, Context
from homebot.processors.base import RegexProcessor
from homebot.services.hass import HassApi
from homebot.validator import attrs_assert_type


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


class OnOffSwitch(RegexProcessor):
    """Home assistant on/off switching component for entities."""
    DEFAULT_COMMAND = 'switch'
    MESSAGE_REGEX = r'^\s*{command}\s+(?P<mode>on|off)\s+(?P<domain>\w+)\.(?P<entity>\w+)\s*$'

    def __init__(self, base_url: str, token: str, timeout: float = 5.0, **kwargs: Any):
        super().__init__(**kwargs)
        self.api = HassApi(base_url, token, timeout)

    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(
            command=str(self.command),
            usage=f"{self.command} on|off <domain>.<entity>",
            description="Calls home assistant to turn on resp. off the passed entity."
        )

    async def __call__(self, ctx: Context, payload: MessageIncoming) -> Iterable[HassStateChange]:
        match = await super().__call__(ctx, payload)
        mode = str(match.group('mode')).strip()
        domain = str(match.group('domain')).strip()
        entity = str(match.group('entity')).strip()

        if mode.lower() == 'on':
            endpoint = 'services/homeassistant/turn_on'
        else:
            endpoint = 'services/homeassistant/turn_off'

        data = {'entity_id': f'{domain}.{entity}'}
        res = await self.api.call(endpoint, method=HassApi.METHOD_POST, data=data)

        return HassStateChange.from_api_response(res)
