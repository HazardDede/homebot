"""Base classes for actions. Actions do something with the payload produced from either
message processors or formatters."""
from typing import Any

from homebot.models import Context
from homebot.utils import AutoStrMixin, LogMixin
from homebot.validator import TypeGuardMeta


class Action(AutoStrMixin, LogMixin, metaclass=TypeGuardMeta):
    """Action base class. Provides the interface to respect."""
    async def __call__(self, ctx: Context, payload: Any) -> None:
        """Performs the action."""
        raise NotImplementedError()  # pragma: no cover


class Console(Action):
    """Simply logs the payload to the console."""
    async def __call__(self, ctx: Context, payload: Any) -> None:
        """Performs the action: Simply print the payload to the console via print."""
        print("Context:", ctx, "\nPayload:", payload)  # pragma: no cover
