"""Contains base classes for Formatters. Formatters do format payloads produced by
message processors."""
from typing import Any, cast


class Formatter:
    """Base class for all formatters. Introduces the interface to respect."""

    def __init__(self, **kwargs: Any):
        super().__init__()

        for key, _ in kwargs.items():
            # TODO: Logging
            print(f"Argument '{key}' is unused")

    def __call__(self, payload: Any) -> Any:
        """Performs the formatting."""
        return payload


class StringFormat(Formatter):
    """Formats the payload by using the passed format."""
    def __init__(self, formatting: str, **kwargs: Any):
        super().__init__(**kwargs)
        self._format = str(formatting)

    def _process(self, payload: Any) -> str:  # pylint: disable=unused-argument
        return cast(str, eval(f'f{self._format!r}'))  # pylint: disable=eval-used

    def __call__(self, payload: Any) -> Any:
        return super().__call__(self._process(payload))
