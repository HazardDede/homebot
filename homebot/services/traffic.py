"""Traffic related services."""
import asyncio
from datetime import datetime, timedelta
from typing import Iterable, Any, Dict, cast, List

import attr
from schiene import Schiene  # type: ignore
from typeguard import typechecked

from homebot.utils import AutoStrMixin
from homebot.validator import attrs_assert_type


@attr.s
class TrafficConnection:
    """Traffic connection data container."""
    # TODO: Typing
    # TODO: Maybe parsing arrival / departure into real time
    # TODO: Maybe parsing travel_time into duration
    arrival: str = attr.ib()
    canceled: bool = attr.ib()
    departure: str = attr.ib()
    products: List[str] = attr.ib()
    transfers: int = attr.ib()
    travel_time: str = attr.ib()
    delayed: bool = attr.ib()
    delay_departure: int = attr.ib()
    delay_arrival: int = attr.ib()


@attr.s
class TrafficInfo:
    """Traffic info (multiple connections) data container."""
    origin: str = attr.ib(validator=attrs_assert_type(str))
    destination: str = attr.ib(validator=attrs_assert_type(str))

    connections: Iterable[TrafficConnection] = attr.ib(
        validator=attrs_assert_type(Iterable[TrafficConnection])
    )


class TrafficService(AutoStrMixin):
    """Base traffic service. Defines the interface to respect."""

    def __init__(self) -> None:
        self.pull = typechecked(always=True)(self.pull)  # type: ignore

    async def pull(  # pylint: disable=method-hidden
            self, origin: str, destination: str, only_direct: bool = False,
            offset: int = 0
    ) -> TrafficInfo:
        """Pulls the data from the service."""
        raise NotImplementedError()  # pragma: no cover


class DeutscheBahn(TrafficService):
    """Pulls the next trains that start from the origin destined for the given
    destination."""

    @classmethod
    async def _mk_conn(
            cls, payload: Dict[str, Any]
    ) -> TrafficConnection:
        return TrafficConnection(
            arrival=str(payload.get('arrival', '')),
            canceled=bool(payload.get('canceled', False)),
            departure=str(payload.get('departure', '')),
            products=cast(List[str], payload.get('products')),
            transfers=int(payload.get('transfers', 0)),
            travel_time=str(payload.get('time', '')),
            delayed=not bool(payload.get('ontime', True)),
            delay_departure=int(payload.get('delay', {}).get('delay_departure', 0)),
            delay_arrival=int(payload.get('delay', {}).get('delay_arrival', 0))
        )

    def _connections(
            self, origin: str, destination: str, offset: int, only_direct: bool
    ) -> Iterable[Dict[str, Any]]:
        api = Schiene()
        connections = api.connections(
            origin,
            destination,
            only_direct=only_direct,
            dt=(datetime.now() + timedelta(minutes=offset))
        )
        return cast(Iterable[Dict[str, Any]], connections)

    async def pull(  # pylint: disable=method-hidden
            self, origin: str, destination: str, only_direct: bool = False,
            offset: int = 0
    ) -> TrafficInfo:
        origin = str(origin)
        destination = str(destination)
        only_direct = bool(only_direct)

        loop = asyncio.get_event_loop()
        connections = await loop.run_in_executor(
            None, self._connections,
            origin, destination, offset, only_direct
        )
        parsed_connections = [
            await self._mk_conn(conn)
            for conn in connections
        ]
        return TrafficInfo(
            origin=origin,
            destination=destination,
            connections=parsed_connections
        )
