"""Traffic related services."""
import asyncio
from datetime import datetime, timedelta
from typing import Iterable, Any, Dict, cast, List

from schiene import Schiene  # type: ignore

from homebot.models import TrafficInfo
from homebot.services.base import TrafficService


class DeutscheBahn(TrafficService):
    """Pulls the next trains that start from the origin destined for the given
    destination."""

    @classmethod
    async def _mk_info(
            cls, payload: Dict[str, Any], origin: str, destination: str
    ) -> TrafficInfo:
        return TrafficInfo(
            origin=origin,
            destination=destination,
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
    ) -> Iterable[TrafficInfo]:
        origin = str(origin)
        destination = str(destination)
        only_direct = bool(only_direct)

        loop = asyncio.get_event_loop()
        connections = await loop.run_in_executor(
            None, self._connections,
            origin, destination, offset, only_direct
        )
        return [
            await self._mk_info(conn, origin, destination)
            for conn in connections
        ]
