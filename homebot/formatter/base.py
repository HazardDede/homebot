"""Contains base classes for Formatters. Formatters do format payloads produced by
message processors."""
from typing import Any

from homebot.models import Message
from homebot.utils import AutoStrMixin, LogMixin, interpolate
from homebot.validator import TypeGuardMeta


class Formatter(AutoStrMixin, LogMixin, metaclass=TypeGuardMeta):
    """Base class for all formatters. Introduces the interface to respect."""

    async def __call__(self, message: Message, payload: Any) -> Any:
        """Performs the formatting."""
        raise NotImplementedError()


class StringFormat(Formatter):
    """Formats the payload by using the passed format.

    Example:

        >>> import asyncio
        >>> dut = StringFormat("This is the number: {payload}")
        >>> msg = Message(text="", origin="", origin_user="", direct_mention=True)
        >>> asyncio.run(dut(msg, 42))
        'This is the number: 42'
    """

    def __init__(self, formatting: str):
        self._format = str(formatting)

    async def __call__(self, message: Message, payload: Any) -> str:
        return interpolate(self._format, message=message, payload=payload)
