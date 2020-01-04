"""Contains listener base classes. Listeners do produce messages to process."""
import asyncio
from typing import Optional

from typeguard import check_type

from homebot.models import ListenerCallback, Incoming
from homebot.utils import AutoStrMixin, LogMixin
from homebot.validator import TypeGuardMeta


class Listener(AutoStrMixin, LogMixin, metaclass=TypeGuardMeta):
    """Base class for listeners. Defines the interface to respect."""

    def __init__(self) -> None:
        self._callback: Optional[ListenerCallback] = None

    @property
    def callback(self) -> Optional[ListenerCallback]:
        """Return the callback."""
        return self._callback

    @callback.setter
    def callback(self, value: ListenerCallback) -> None:
        """Set the callback function. This is where the listener will send incoming
        messages."""
        check_type('value', value, ListenerCallback)  # type: ignore
        self._callback = value

    async def _fire_callback(self, incoming: Incoming) -> None:
        """Helper method to trigger the callback with the given message."""
        if not self._callback:
            return
        try:
            asyncio.create_task(self._callback(incoming))
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Error caught during execution of callback")

    async def start(self) -> None:
        """Run the listener."""
        raise NotImplementedError()  # pragma: no cover
