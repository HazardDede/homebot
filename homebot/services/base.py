"""Contains base services."""
from typing import Iterable

from homebot.models import TrafficInfo
from homebot.utils import AutoStrMixin


class TrafficService(AutoStrMixin):
    """Base traffic service. Defines the interface to respect."""
    async def pull(
            self, origin: str, destination: str, only_direct: bool = False,
            offset: int = 0
    ) -> Iterable[TrafficInfo]:
        """Pulls the data from the service."""
        raise NotImplementedError()
