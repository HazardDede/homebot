"""Contains base classes for formatting payloads."""
import os
from typing import Any

from homebot.formatter.base import Formatter
from homebot.models import Message, SlackMessageTemplate, SlackMessage


class Codify(Formatter):
    """Adds code backticks to the payload."""
    # TODO: Add support for SlackMessage
    async def __call__(self, message: Message, payload: Any) -> str:
        return f"```{str(payload)}```"


class Mention(Formatter):
    """Adds <@user> mention to the payload."""
    # TODO: Add support for SlackMessage
    async def __call__(self, message: Message, payload: Any) -> str:
        user_id = message.origin_user
        if not user_id:
            return str(payload)  # No user to mention
        return f"<@{user_id}> {str(payload)}"


class Template(Formatter):
    """Augments a slack block layout provided by the user."""
    def __init__(self, template: SlackMessageTemplate):
        self.template = template

    @classmethod
    def from_file(cls, file_path: str) -> 'Template':
        """Loads the layout from a json file and instantiates an instance."""
        ext_mapping = {
            '.json': SlackMessageTemplate.from_json,
            '.mako': SlackMessageTemplate.from_mako,
            '.tpl': SlackMessageTemplate.from_mako
        }
        _, ext = os.path.splitext(file_path)
        factory = ext_mapping.get(ext)
        if not factory:
            raise NotImplementedError(f"Template extension '{ext}' is not supported")
        return cls(factory(file_path))

    async def __call__(self, message: Message, payload: Any) -> SlackMessage:
        return self.template.render(message=message, payload=payload)
