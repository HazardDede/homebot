"""Contains base classes for formatting payloads."""
from typing import Any, overload, Union

from homebot.formatter.base import Formatter
from homebot.models import SlackMessageTemplate, SlackMessage, Context


class Codify(Formatter):
    """Adds code backticks to the payload."""
    @overload
    async def __call__(self, ctx: Context, payload: SlackMessage) -> SlackMessage:  # type: ignore
        ...

    @overload
    async def __call__(self, ctx: Context, payload: Any) -> str:
        ...

    async def __call__(self, ctx: Context, payload: Union[SlackMessage, Any]) -> Union[SlackMessage, str]:
        if isinstance(payload, SlackMessage):
            if payload.text is None:
                # Nothing to do... Will not tamper with blocks and attachments
                return payload
            payload.text = f"```{payload.text}```"
            return payload

        return f"```{str(payload)}```"


class Template(Formatter):
    """Augments a slack block layout provided by the user."""
    def __init__(self, template: SlackMessageTemplate):
        self.template = template

    @classmethod
    def from_file(cls, file_path: str) -> 'Template':
        """Loads the layout from a json file and instantiates an instance."""
        return cls(SlackMessageTemplate.from_file(file_path))

    async def __call__(self, ctx: Context, payload: Any) -> SlackMessage:
        return self.template.render(ctx=ctx, payload=payload)
