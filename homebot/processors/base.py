"""Contains message processor base classes. Processors do process messages produced by
listeners."""
import re
from typing import Any, Optional, Iterable, Match

from homebot.models import HelpEntry, Message


class Processor:
    """Base class for message processors."""

    DEFAULT_COMMAND: Optional[str] = None  # Default command when not passed via initializer
    VALID_COMMAND_PATTERN = r'^[!a-z]\w+$'

    def __init__(self, command: Optional[str] = None):
        self.orchestrator: Optional['Orchestrator'] = None  # type: ignore
        self._command = command or self.DEFAULT_COMMAND
        if not self._command:
            raise ValueError("Argument 'command' is unset. Please pass per initializer.")
        self._command = str(self._command).strip().lower()
        valid_cmd = re.match(self.VALID_COMMAND_PATTERN, self._command)
        if not valid_cmd:
            raise ValueError(f"Argument 'command' ('{self._command}') is not a valid command.")
        self._command = re.escape(self._command)

    def help(self) -> HelpEntry:
        """Return the help entry for this processor."""
        return HelpEntry(
            command=str(self._command),
            usage=str(self._command),
            description=""
        )

    def can_process(self, message: Message) -> bool:
        """Checks if the processor can process the given message."""
        raise NotImplementedError()

    def __call__(self, message: Message) -> Any:
        """Process the given message."""
        raise NotImplementedError()


class RegexProcessor(Processor):
    """Regex-powered processor to parse messages.
    You have to implement the `MESSAGE_REGEX` and the method `_matched` in subclasses."""
    MESSAGE_REGEX = r'^\s*{command}\s*$'

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._regex = re.compile(
            self.MESSAGE_REGEX.format(command=self._command),
            re.IGNORECASE
        )

    def _try_match(self, message: Message) -> Optional[Match[str]]:
        return self._regex.match(message.text)

    def can_process(self, message: Message) -> bool:
        return self._try_match(message) is not None

    def __call__(self, message: Message) -> Any:
        match = self._try_match(message)
        if not match:
            return None
        return self._matched(message, match)

    def _matched(self, message: Message, match: Match[str]) -> Any:
        """Processes the matched message. The regex match will be passed as well."""
        raise NotImplementedError()


class Help(RegexProcessor):
    """Provides a command (!help) to collect all help entries of the processors of the
    orchestrator and return them."""

    DEFAULT_COMMAND = 'help'

    def help(self) -> HelpEntry:
        res = super().help()
        res.description = "Shows this help page."
        return res

    def _collect(self) -> Iterable[HelpEntry]:
        """Collects all the help entries of all message processors for the current
        orchestra."""
        # pylint: disable=protected-access
        if not self.orchestrator or not self.orchestrator._flows:
            return [self.help()]

        return [handler.processor.help() for handler in self.orchestrator._flows]
        # pylint: enable=protected-access

    def _matched(self, message: Message, match: Match[str]) -> Any:
        return self._collect()


class Version(RegexProcessor):
    """Provides a command (!version) to collect the current homebot version."""

    DEFAULT_COMMAND = 'version'

    def help(self) -> HelpEntry:
        res = super().help()
        res.description = "Shows the version of homebot."
        return res

    def _version(self) -> str:
        """Collects all the help entries of all message processors for the current
        orchestra."""
        _ = self
        from homebot.config import __VERSION__
        return __VERSION__

    def _matched(self, message: Message, match: Match[str]) -> Any:
        return self._version()
