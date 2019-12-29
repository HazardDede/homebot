"""Contains base classes for Formatters. Formatters do format payloads produced by
message processors."""
from typing import Any

from homebot.models import Context
from homebot.utils import AutoStrMixin, LogMixin, interpolate
from homebot.validator import TypeGuardMeta


class Formatter(AutoStrMixin, LogMixin, metaclass=TypeGuardMeta):
    """Base class for all formatters. Introduces the interface to respect."""

    async def __call__(self, ctx: Context, payload: Any) -> Any:
        """Performs the formatting."""
        raise NotImplementedError()


class StringFormat(Formatter):
    """Formats the payload by using the passed format.

    Example:

        >>> import asyncio
        >>> from homebot.models import Payload
        >>> dut = StringFormat("This is the number: {payload}")
        >>> asyncio.run(dut(Context(Payload()), 42))
        'This is the number: 42'
    """

    def __init__(self, formatting: str):
        self._format = str(formatting)

    async def __call__(self, ctx: Context, payload: Any) -> str:
        return interpolate(self._format, ctx=ctx, payload=payload)
