"""Slack related actions."""
from typing import Any, Dict

import slack  # type: ignore

from homebot.actions.base import Action
from homebot.models import SlackMessage, MessageIncoming, Context


class SendMessage(Action):
    """Posts the payload to slack."""

    def __init__(self, token: str):
        self._client = slack.WebClient(
            token=token,
            run_async=True
        )

    async def __call__(self, ctx: Context, payload: Any) -> None:
        """Performs the action. Sends the payload to a slack channel."""
        if not isinstance(ctx.incoming, MessageIncoming):
            raise RuntimeError("The source payload does not provide a destination channel.")

        args: Dict[str, Any] = {'channel': ctx.incoming.origin}

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
