"""Home assistant related processors."""
from typing import Any, Iterable, Optional

from homebot.models import HelpEntry, HassStateChange, Message, Context
from homebot.processors.base import RegexProcessor
from homebot.services.hass import HassApi


class OnOffSwitch(RegexProcessor):
    """Home assistant on/off switching component for entities."""
    DEFAULT_COMMAND = 'switch'
    MESSAGE_REGEX = r'^\s*{command}\s+(?P<mode>on|off)\s+(?P<domain>\w+)\.(?P<entity>\w+)$'

    def __init__(self, base_url: str, token: str, timeout: float = 5.0, **kwargs: Any):
        super().__init__(**kwargs)
        self.api = HassApi(base_url, token, timeout)

    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(
            command=str(self.command),
            usage=f"{self.command} on|off <domain>.<entity>",
            description="Calls home assistant to turn on resp. off the passed entity."
        )

    async def __call__(self, ctx: Context, payload: Message) -> Iterable[HassStateChange]:
        match = await super().__call__(ctx, payload)
        mode = match.group('mode')
        domain = match.group('domain')
        entity = match.group('entity')

        if mode.lower() == 'on':
            endpoint = 'services/homeassistant/turn_on'
        else:
            endpoint = 'services/homeassistant/turn_off'

        data = {'entity_id': f'{domain}.{entity}'}
        res = await self.api.call(endpoint, method=HassApi.METHOD_POST, data=data)

        return [
            HassStateChange(
                friendly_name=item.get('attributes', {}).get('friendly_name', ''),
                entity_id=item.get('entity_id', ''),
                state=item.get('state', 'unknown')
            )
            for item in res
        ]
