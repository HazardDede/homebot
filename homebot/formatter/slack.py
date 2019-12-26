"""Contains base classes for formatting payloads."""
from typing import Any

from typeguard import typechecked

from homebot.formatter.base import Formatter


class Codify(Formatter):
    """Adds code backticks to the payload."""

    @typechecked(always=True)
    async def __call__(self, payload: Any) -> Any:
        return await super().__call__(f"```{str(payload)}```")
