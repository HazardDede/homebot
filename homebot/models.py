"""Application models (beans, containers, whatever you may call it)."""

import copy
from typing import List, Callable, Awaitable

import attr


@attr.s
class Message:
    """A message returned from a listener."""
    text: str = attr.ib()
    origin: str = attr.ib()
    direct_mention: bool = attr.ib(default=False)

    def clone(self) -> 'Message':
        """Clones this instance."""
        return copy.copy(self)


@attr.s
class HelpEntry:
    """A help entry from a message processor."""
    command: str = attr.ib()
    usage: str = attr.ib()
    description: str = attr.ib()


@attr.s
class TrafficInfo:
    """Traffic info data container."""
    # TODO: Typing
    # TODO: Maybe parsing arrival / departure into real time
    # TODO: Maybe parsing travel_time into duration
    origin: str = attr.ib()
    destination: str = attr.ib()
    arrival: str = attr.ib()
    canceled: bool = attr.ib()
    departure: str = attr.ib()
    products: List[str] = attr.ib()
    transfers: int = attr.ib()
    travel_time: str = attr.ib()
    delayed: bool = attr.ib()
    delay_departure: int = attr.ib()
    delay_arrival: int = attr.ib()


ListenerCallback = Callable[[Message], Awaitable[None]]
