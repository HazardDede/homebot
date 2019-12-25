"""Contains base classes for formatting payloads."""
from typing import Any, List

from homebot.formatter.base import Formatter
from homebot.models import TrafficInfo


class _TrafficFormatter(Formatter):
    """Base class for all traffic formatters."""
    async def __call__(self, payload: Any) -> Any:
        return await super().__call__(await self._format(payload))

    async def _format(self, info: List[TrafficInfo]) -> str:
        """Implement in derived classes to format a list of `TrafficInfo`."""
        raise NotImplementedError()


class PlainText(_TrafficFormatter):
    """Simple text formatting of a traffic info. Result will look like this:
    origin -> destination
    RE: 06:38 - 07:06 (+0)
    NBE: 07:06 - 07:37 (+0)
    RE: 07:19 - 07:46 (+0)

    Or in more general:
    <products>: <departure> - <arrival> (+<delay>)
    """

    def __init__(self, layout: str = 'simple', **kwargs: Any):
        super().__init__(**kwargs)
        self._layout = layout

    async def _format_item(self, item: TrafficInfo) -> str:
        if self._layout.lower() == 'simple':
            return f"{','.join(item.products)}: {item.departure} - {item.arrival} " \
                f"(+{item.delay_arrival})"
        if self._layout.lower() == 'delays':
            return f"{','.join(item.products)}: {item.departure} (+{item.delay_arrival})"

        raise NotImplementedError(f"Layout '{self._layout}' is not supported.")

    async def _format(self, info: List[TrafficInfo]) -> str:
        if not info:
            return ""
        first = info[0]
        header = f"{first.origin} -> {first.destination}"
        lines = [await self._format_item(item) for item in info]

        return "\n".join([header] + lines)
