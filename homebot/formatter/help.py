"""HelpEntry related formatters."""

from textwrap import wrap
from typing import Any, Iterable

from terminaltables import AsciiTable  # type: ignore
from typeguard import typechecked

from homebot.formatter.base import Formatter
from homebot.models import HelpEntry


class TextTable(Formatter):
    """Transforms an iterable of help entries into a text table representation."""

    @typechecked(always=True)
    def __init__(self, usage_width: int = 40, description_width: int = 80,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.usage_width = usage_width
        self.description_width = description_width

    @typechecked(always=True)
    async def __call__(self, payload: Iterable[HelpEntry]) -> Any:
        # TODO: Check payload for iterable of HelpEntry
        rows = [
            [
                h.command,
                # h.usage,
                # h.description
                "\n".join(wrap(h.usage, width=40)),
                "\n".join(wrap(h.description, width=80))
            ]
            for h in payload
        ]
        data = [['Command', 'Usage', 'Description']] + rows
        table = AsciiTable(data)
        table.inner_row_border = True

        return await super().__call__(table.table)
