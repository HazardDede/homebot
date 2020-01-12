"""Contains base services."""
import attr

from homebot.utils import AutoStrMixin, LogMixin


class LocationResolutionError(Exception):
    """Is raised when the location of a person cannot be determined."""


@attr.s
class Location:
    """Represents a person's location. """
    name: str = attr.ib()


class LocationService(AutoStrMixin, LogMixin):
    """Base class for location services."""

    async def is_home(self, name: str) -> bool:
        """Returns True if the person with the specified name is home; otherwise False."""
        raise NotImplementedError()

    async def is_away(self, name: str) -> bool:
        """Returns True if the person with the specified name is away; otherwise False."""
        raise NotImplementedError()

    async def location(self, name: str) -> Location:
        """Returns the location of the person with the specified name."""
        raise NotImplementedError()
