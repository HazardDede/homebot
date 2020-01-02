"""Contains base services."""

from typeguard import typechecked

from homebot.models import TrafficInfo
from homebot.utils import AutoStrMixin


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
