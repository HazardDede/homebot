"""Slack related actions."""
from typing import Any, Dict

import slack  # type: ignore

from homebot.actions.base import Action
from homebot.models import Message, SlackMessage


class SendMessage(Action):
    """Posts the payload to slack."""

    def __init__(self, token: str):
        self._client = slack.WebClient(
            token=token,
            run_async=True
        )

    async def __call__(self, message: Message, payload: Any) -> None:
        """Performs the action. Sends the payload to a slack channel."""
        args: Dict[str, Any] = {'channel': message.origin}

        if isinstance(payload, SlackMessage):
            args = {
                'blocks': payload.blocks,
                'attachments': payload.attachments,
                'text': payload.text,
                **args
            }
        else:
            args = {'text': str(payload), **args}

        await self._client.chat_postMessage(**args)
