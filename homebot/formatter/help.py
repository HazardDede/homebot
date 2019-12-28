"""HelpEntry related formatters."""

from textwrap import wrap
from typing import Iterable

from terminaltables import AsciiTable  # type: ignore

from homebot.formatter.base import Formatter
from homebot.models import HelpEntry, Message


class TextTable(Formatter):
    """Transforms an iterable of help entries into a text table representation."""

    def __init__(self, usage_width: int = 40, description_width: int = 80):
        self.usage_width = usage_width
        self.description_width = description_width

    async def __call__(self, message: Message, payload: Iterable[HelpEntry]) -> str:
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

        return str(table.table)
