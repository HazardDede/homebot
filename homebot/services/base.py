"""Contains base services."""
from typing import Iterable

from homebot.models import TrafficInfo


class TrafficService:
    """Base traffic service. Defines the interface to respect."""
    def pull(self, origin: str, destination: str, only_direct: bool = False,
             offset: int = 0) -> Iterable[TrafficInfo]:
        """Pulls the data from the service."""
        raise NotImplementedError()
