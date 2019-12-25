"""Contains processors for retrieving traffic information."""
from typing import Any, Iterable, Match

from homebot.models import HelpEntry, Message, TrafficInfo
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

    async def help(self) -> HelpEntry:
        return HelpEntry(
            command=str(self._command),
            usage="{} <origin> to <destination> [+offset]".format(self._command),
            description="Queries the Deutsche Bahn API for connections between "
                        "the origin and the destination. Optionally you can pass a "
                        "offset for the time in minutes. If no offset is passed "
                        "it will be set to 0 minutes (which means now)."
        )

    async def _call_service(self, match: Match[str]) -> Iterable[TrafficInfo]:
        """Calls the traffic service to retrieve the traffic infos."""
        source = match.group('source').strip()
        target = match.group('target').strip()
        offset = int(match.group('offset') or 0)

        return await self._service.pull(source, target, offset=offset)

    async def _matched(self, message: Message, match: Match[str]) -> Any:
        return await self._call_service(match)
