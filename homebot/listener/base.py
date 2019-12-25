"""Contains listener base classes. Listeners do produce messages to process."""
import traceback
from typing import Optional

from homebot.models import ListenerCallback, Message


class Listener:
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
        self._callback = value

    async def _fire_callback(self, message: Message) -> None:
        """Helper method to trigger the callback with the given message."""
        if not self._callback:
            return
        try:
            await self._callback(message)
        except Exception:  # pylint: disable=broad-except
            print(traceback.format_exc())

    async def start(self) -> None:
        """Run the listener."""
        raise NotImplementedError()
