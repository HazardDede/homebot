"""Contains message processor base classes. Processors do process messages produced by
listeners."""
import re
from typing import Any, Optional, Iterable, Match

from homebot.models import HelpEntry, Payload, Message, Context, ErrorPayload, \
    UnknownCommandPayload
from homebot.utils import AutoStrMixin, LogMixin
from homebot.validator import TypeGuardMeta


class Processor(AutoStrMixin, LogMixin, metaclass=TypeGuardMeta):
    """Base class for message processors."""

    def __init__(self, **kwargs: Any):
        self.orchestrator: Optional['Orchestrator'] = None  # type: ignore

    async def help(self) -> Optional[HelpEntry]:
        """Return the help entry for this processor."""
        raise NotImplementedError()  # pragma: no cover

    async def can_process(self, payload: Payload) -> bool:
        """Checks if the processor can process the given message."""
        raise NotImplementedError()  # pragma: no cover

    # We need to type payload with Any. Otherwise the typing of the childs will be invalid
    async def __call__(self, ctx: Context, payload: Any) -> Any:
        """Process the given message."""
        raise NotImplementedError()  # pragma: no cover


class Error(Processor):
    """Processor to handle the ErrorPayload."""

    async def help(self) -> Optional[HelpEntry]:
        return None

    async def can_process(self, payload: Payload) -> bool:
        return isinstance(payload, ErrorPayload)

    async def __call__(self, ctx: Context, payload: ErrorPayload) -> ErrorPayload:
        return payload


class UnknownCommand(Processor):
    """Processor to handle the an unknown command."""

    async def help(self) -> Optional[HelpEntry]:
        return None

    async def can_process(self, payload: Payload) -> bool:
        return isinstance(payload, UnknownCommandPayload)

    async def __call__(self, ctx: Context, payload: UnknownCommandPayload) -> UnknownCommandPayload:
        return payload


class RegexProcessor(Processor):
    """Regex-powered processor to parse messages.
    You have to implement the `MESSAGE_REGEX` and the method `_matched` in subclasses."""

    DEFAULT_COMMAND: Optional[str] = None  # Default command when not passed via initializer
    VALID_COMMAND_PATTERN = r'^\w[\w \d]+$'
    MESSAGE_REGEX = r'^\s*{command}\s*$'

    def __init__(self, command: Optional[str] = None, **kwargs: Any):
        super().__init__(**kwargs)

        self.command = command or self.DEFAULT_COMMAND
        if not self.command:
            raise ValueError("Argument 'command' is unset. Please pass by initializer.")
        self.command = str(self.command).strip().lower()
        valid_cmd = re.match(self.VALID_COMMAND_PATTERN, self.command)
        if not valid_cmd:
            raise ValueError(f"Argument 'command' ('{self.command}') is not a valid command.")

        self._regex = re.compile(
            self.MESSAGE_REGEX.format(command=re.escape(self.command)),
            re.IGNORECASE
        )

    async def help(self) -> Optional[HelpEntry]:
        """Return the help entry for this processor."""
        return HelpEntry(
            command=str(self.command),
            usage=str(self.command),
            description=""
        )

    async def _try_match(self, message: Message) -> Optional[Match[str]]:
        return self._regex.match(message.text)

    async def can_process(self, payload: Payload) -> bool:
        if not isinstance(payload, Message):
            return False
        return await self._try_match(payload) is not None

    async def __call__(self, ctx: Context, payload: Message) -> Any:
        match = await self._try_match(payload)
        if not match:
            raise RuntimeError(
                "Processor is called with a message that is not supported. "
                "Call `can_process(...)` first to make sure the incoming is supported."
            )
        return match


class Help(RegexProcessor):
    """Provides a command (!help) to collect all help entries of the processors of the
    orchestrator and return them."""

    DEFAULT_COMMAND = 'help'

    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(
            command=str(self.command),
            usage=str(self.command),
            description="Shows this help page."
        )

    async def _collect(self) -> Iterable[HelpEntry]:
        """Collects all the help entries of all message processors for the current
        orchestra."""
        if not self.orchestrator or not self.orchestrator.flows:
            this_help = await self.help()
            return [this_help] if this_help else []

        entries = [await handler.processor.help() for handler in self.orchestrator.flows]
        return [entry for entry in entries if entry]  # Only non None

    async def __call__(self, ctx: Context, payload: Message) -> Iterable[HelpEntry]:
        await super().__call__(ctx, payload)
        return await self._collect()


class Version(RegexProcessor):
    """Provides a command (!version) to collect the current homebot version."""

    DEFAULT_COMMAND = 'version'

    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(
            command=str(self.command),
            usage=str(self.command),
            description="Shows the version of homebot."
        )

    async def __call__(self, ctx: Context, payload: Message) -> str:
        await super().__call__(ctx, payload)
        from homebot.config import __VERSION__
        return __VERSION__
