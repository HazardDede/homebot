"""Slack related listener."""
import re
from typing import Dict, Any, Pattern

import slack  # type: ignore
from async_property import async_cached_property  # type: ignore

from homebot.listener.base import Listener, ListenerError
from homebot.models import MessageIncoming


class DirectMention(Listener):
    """Listens for direct mentions of the bot in slack channels."""
    DIRECT_MENTION_REGEX = r'^\<\@{id}\>'

    def __init__(self, token: str):
        super().__init__()
        self._token = token
        self._client = slack.RTMClient(
            token=self._token,
            run_async=True
        )

    @async_cached_property  # type: ignore
    async def bot_user_id(self) -> str:
        """Return the id of the bot."""
        client = slack.WebClient(self._token, run_async=True)
        resp = await client.auth_test()
        if resp.get('ok', False):
            user_id = str(resp.get('user_id'))
            self.logger.debug("Retrieved bot user_id from slack: %s", user_id)
            return user_id
        raise ListenerError("Failed to retrieve the slack user_id of the bot.")

    @async_cached_property  # type: ignore
    async def mention_regex(self) -> Pattern[str]:
        """Return the mention regex. Specifies how to identify a direct mention message."""
        return re.compile(
            self.DIRECT_MENTION_REGEX.format(id=await self.bot_user_id)
        )

    async def _on_message(self, data: Dict[str, Any], **unused: Any) -> None:
        """Callback that is called on every message. The message text will be parsed
        for a direct mention of the bot and only those with direct mentions will be
        delegated to the processing flow."""
        _ = unused  # Fake usage

        message = None
        message_text = data.get('text')
        channel = data.get('channel')
        user_id = data.get('user')
        if not message_text:
            return

        mention_match = (await self.mention_regex).match(message_text)
        if mention_match:
            _, last = mention_match.span()
            message = MessageIncoming(
                text=message_text[last:].strip(),
                origin=str(channel),
                origin_user=str(user_id),
                direct_mention=True
            )

        if message:
            await self._fire_callback(message)

    async def start(self) -> None:
        self._client.on(
            event='message',
            callback=self._on_message
        )
        await self._client.start()
