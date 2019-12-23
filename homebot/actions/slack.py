"""Slack related actions."""
from typing import Any, Iterable

import slack  # type: ignore

from homebot.actions.base import Action
from homebot.models import HelpEntry, Message


class SendMessage(Action):
    """Posts the payload to slack."""
    def __init__(self, token: str):
        self._client = slack.WebClient(token=token)

    @staticmethod
    def _create_help(messages: Iterable[HelpEntry]) -> str:
        """Helper to send help messages to slack"""
        from terminaltables import AsciiTable  # type: ignore
        from textwrap import wrap

        rows = [
            [
                h.command,
                # h.usage,
                # h.description
                "\n".join(wrap(h.usage, width=40)),
                "\n".join(wrap(h.description, width=80))
            ]
            for h in messages
        ]
        data = [['Command', 'Usage', 'Description']] + rows
        table = AsciiTable(data)
        table.inner_row_border = True

        return f"```{table.table}```"

    def __call__(self, message: Message, payload: Any) -> None:
        """Performs the action. Sends the payload to a slack channel."""
        # TODO: Put this into utils
        if isinstance(payload, HelpEntry):
            payload = self._create_help([payload])
        if isinstance(payload, list) and payload and isinstance(payload[0], HelpEntry):
            payload = self._create_help(payload)

        if not isinstance(payload, str):
            payload = str(payload)

        self._client.chat_postMessage(
            text=payload,
            channel=message.origin
        )
