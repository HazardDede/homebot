"""Home assistant related processors."""
from typing import Any, Iterable, Optional

from homebot.models import HelpEntry, MessageIncoming, Context
from homebot.processors.base import RegexProcessor
from homebot.services.hass import HassApi, HassStateChange


class OnOffSwitch(RegexProcessor):
    """Home assistant on/off switching component for entities."""
    DEFAULT_COMMAND = 'hass switch'
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

        return await self.api.switch_on_off(domain, entity, mode.lower() == 'on')  # type: ignore
