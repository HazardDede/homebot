"""Slack related actions."""
from typing import Any

import slack  # type: ignore
from typeguard import typechecked

from homebot.actions.base import Action
from homebot.models import Message


class SendMessage(Action):
    """Posts the payload to slack."""

    @typechecked(always=True)
    def __init__(self, token: str):
        self._client = slack.WebClient(
            token=token,
            run_async=True
        )

    @typechecked(always=True)
    async def __call__(self, message: Message, payload: Any) -> None:
        """Performs the action. Sends the payload to a slack channel."""
        if not isinstance(payload, str):
            payload = str(payload)

        await self._client.chat_postMessage(
            text=payload,
            channel=message.origin
        )
