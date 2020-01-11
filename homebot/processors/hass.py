"""Home assistant related processors."""
from typing import Any, Iterable, Optional

from homebot.models import HelpEntry, MessageIncoming, Context
from homebot.processors.base import RegexProcessor
from homebot.services.hass import HassApi, HassStateChange, HassEntity


class _HassBase(RegexProcessor):
    """Base class for home assistant api related processors."""
    def __init__(self, base_url: str, token: str, timeout: float = 5.0, **kwargs: Any):
        super().__init__(**kwargs)
        self.api = HassApi(base_url, token, timeout)


class OnOffSwitch(_HassBase):
    """Home assistant on/off switching component for entities."""
    DEFAULT_COMMAND = 'hass switch'
    MESSAGE_REGEX = r'^\s*{command}\s+(?P<mode>on|off)\s+(?P<domain>\w+)\.(?P<entity>\w+)\s*$'

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

        return await self.api.switch_on_off(domain, entity, mode.lower() == 'on')  # type: ignore


class Entities(_HassBase):
    """Home assistant processor to retrieve entities via rest endpoint."""
    DEFAULT_COMMAND = 'hass entity'
    MESSAGE_REGEX = r'^\s*{command}(\s+(?P<entity_pattern>[\w\.\*\?]+))?\s*$'

    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(
            command=str(self.command),
            usage=f"{self.command}[<entity pattern>]",
            description="Calls home assistant to return entities that match the pattern (use * and ? as wildcard)."
                        "If no pattern is given all entities will be returned."
                        "The pattern can be prefixed by a domain to only search in that domain."
        )

    async def __call__(self, ctx: Context, payload: MessageIncoming) -> Iterable[HassEntity]:
        match = await super().__call__(ctx, payload)
        entity_pattern = None
        domain = None
        if match.group('entity_pattern'):
            entity_pattern = str(match.group('entity_pattern')).strip()
            if '.' in entity_pattern:
                domain, entity_pattern = entity_pattern.split('.', 1)

        return await self.api.states(domain=domain, entity_pattern=entity_pattern)  # type: ignore
