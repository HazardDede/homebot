"""Contains base classes for formatting payloads."""
from typing import Any

from homebot.formatter.base import Formatter


class Codify(Formatter):
    """Adds code backticks to the payload."""
    def __call__(self, payload: Any) -> Any:
        return super().__call__(f"```{str(payload)}```")
