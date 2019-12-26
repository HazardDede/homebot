"""Contains base classes for Formatters. Formatters do format payloads produced by
message processors."""
from typing import Any, cast

from typeguard import typechecked

from homebot.utils import AutoStrMixin, LogMixin


class Formatter(AutoStrMixin, LogMixin):
    """Base class for all formatters. Introduces the interface to respect."""

    def __init__(self, **kwargs: Any):
        super().__init__()

        for key, _ in kwargs.items():
            # TODO: Logging
            print(f"Argument '{key}' is unused")

    async def __call__(self, payload: Any) -> Any:
        """Performs the formatting."""
        return payload


class StringFormat(Formatter):
    """Formats the payload by using the passed format.

    Example:

        >>> import asyncio
        >>> dut = StringFormat("This is the number: {payload}")
        >>> asyncio.run(dut(42))
        'This is the number: 42'
    """

    @typechecked(always=True)
    def __init__(self, formatting: str, **kwargs: Any):
        super().__init__(**kwargs)
        self._format = str(formatting)

    async def _process(self, payload: Any) -> str:  # pylint: disable=unused-argument
        return cast(str, eval(f'f{self._format!r}'))  # pylint: disable=eval-used

    @typechecked(always=True)
    async def __call__(self, payload: Any) -> Any:
        return await super().__call__(await self._process(payload))
