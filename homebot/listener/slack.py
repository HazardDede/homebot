"""Slack related listener."""

import re
from typing import Dict, Any

import slack  # type: ignore

from homebot.listener.base import Listener
from homebot.models import Message


class DirectMention(Listener):
    """Listens for direct mentions of the bot in slack channels."""
    # MENTION_REGEX = r'\<\@{id}\>'
    DIRECT_MENTION_REGEX = r'^\<\@{id}\>'

    def __init__(self, token: str, bot_id: str):
        super().__init__()
        self._token = token
        self._bot_id = bot_id
        self._client = slack.RTMClient(
            token=self._token
        )
        self._direct_mention_regex = re.compile(
            self.DIRECT_MENTION_REGEX.format(id=self._bot_id))
        # self._mention_regex = re.compile(self.MENTION_REGEX.format(id=self._bot_id))

    def _on_message(self, data: Dict[str, Any], **unused: Any) -> None:  # pylint: disable=unused-argument
        """Callback that is called on every message. The message text will be parsed
        for a direct mention of the bot and only those with direct mentions will be
        delegated to the processing flow."""
        message = None
        message_text = data.get('text')
        channel = data.get('channel')
        if not message_text:
            return

        mention_match = self._direct_mention_regex.match(message_text)
        if mention_match:
            _, last = mention_match.span()
            message = Message(
                text=message_text[last:].strip(),
                origin=str(channel),
                direct_mention=True
            )

        if message:
            self._fire_callback(message)

    def start(self) -> None:
        self._client.on(
            event='message',
            callback=self._on_message
        )
        self._client.start()