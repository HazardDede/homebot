"""Contains processors for retrieving traffic information."""
from typing import Any, Iterable, Optional

from homebot.models import HelpEntry, TrafficInfo, Message, Context
from homebot.processors.base import RegexProcessor
from homebot.services import TrafficService


class Traffic(RegexProcessor):
    """Processes a !traffic command and delegates the work to a traffic service."""
    DEFAULT_COMMAND = 'traffic'
    MESSAGE_REGEX = r'^\s*{command}\s+(?P<source>[\w\d ]+)\s+to\s+' \
                    r'(?P<target>[\w\d ]+)\s*(\+(?P<offset>\d+))?\w*$'

    def __init__(self, service: TrafficService, **kwargs: Any):
        super().__init__(**kwargs)
        self._service = service

    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(
            command=str(self.command),
            usage="{} <origin> to <destination> [+offset]".format(self.command),
            description="Queries the passed traffic service for connections between "
                        "the origin and the destination. Optionally you can pass a "
                        "offset for the time in minutes. If no offset is passed "
                        "it will be set to 0 minutes (which means now)."
        )

    async def __call__(self, ctx: Context, payload: Message) -> Iterable[TrafficInfo]:
        match = await super().__call__(ctx, payload)
        source = match.group('source').strip()
        target = match.group('target').strip()
        offset = int(match.group('offset') or 0)

        return await self._service.pull(source, target, offset=offset)
