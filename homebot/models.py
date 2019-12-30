"""Application models (beans, containers, whatever you may call it)."""

import copy
import json
import os
from typing import List, Callable, Awaitable, Dict, Any, Optional, Iterable

import attr
from mako.template import Template  # type: ignore

from homebot.utils import interpolate_complex
from homebot.validator import attrs_assert_type


@attr.s
class Payload:
    """A payload returned from a listener."""

    def clone(self) -> 'Payload':
        """Clones this instance."""
        return copy.deepcopy(self)


@attr.s
class Message(Payload):
    """A payload returned from a listener."""
    text: str = attr.ib(converter=str)
    origin: str = attr.ib(converter=str)
    origin_user: str = attr.ib(converter=str)
    direct_mention: bool = attr.ib(converter=bool, default=False)


@attr.s
class ErrorPayload(Payload):
    """A payload that contains an error message and a - optional - trace."""
    error_message: str = attr.ib(converter=str)
    trace: str = attr.ib(converter=str, default="No trace")


@attr.s
class UnknownCommandPayload(Payload):
    """A payload that indicates an unknown command."""
    command: str = attr.ib(converter=str)


@attr.s
class Context:
    """Context."""
    original_payload: Payload = attr.ib(validator=attrs_assert_type(Payload))

    def clone(self) -> 'Context':
        """Clones this instance."""
        return copy.deepcopy(self)


ListenerCallback = Callable[[Payload], Awaitable[None]]


@attr.s
class HelpEntry:
    """A help entry from a message processor."""
    command: str = attr.ib(converter=str)
    usage: str = attr.ib(converter=str)
    description: str = attr.ib(converter=str, default="")


@attr.s
class TrafficConnection:
    """Traffic connection data container."""
    # TODO: Typing
    # TODO: Maybe parsing arrival / departure into real time
    # TODO: Maybe parsing travel_time into duration
    arrival: str = attr.ib()
    canceled: bool = attr.ib()
    departure: str = attr.ib()
    products: List[str] = attr.ib()
    transfers: int = attr.ib()
    travel_time: str = attr.ib()
    delayed: bool = attr.ib()
    delay_departure: int = attr.ib()
    delay_arrival: int = attr.ib()


@attr.s
class TrafficInfo:
    """Traffic info (multiple connections) data container."""
    origin: str = attr.ib(validator=attrs_assert_type(str))
    destination: str = attr.ib(validator=attrs_assert_type(str))

    connections: Iterable[TrafficConnection] = attr.ib(
        validator=attrs_assert_type(Iterable[TrafficConnection])
    )


@attr.s
class LegoPricing:
    """Lego pricing data container."""
    set_name: str = attr.ib(validator=attrs_assert_type(str))
    set_id: int = attr.ib(validator=attrs_assert_type(int))
    set_image_url: str = attr.ib(validator=attrs_assert_type(str))
    current: float = attr.ib(validator=attrs_assert_type(float))
    recommended: float = attr.ib(validator=attrs_assert_type(float))
    highest: float = attr.ib(validator=attrs_assert_type(float))
    lowest: float = attr.ib(validator=attrs_assert_type(float))


@attr.s
class HassStateChange:
    """Home assistant state change data container."""
    friendly_name: str = attr.ib(validator=attrs_assert_type(str))
    entity_id: str = attr.ib(validator=attrs_assert_type(str))
    state: str = attr.ib(validator=attrs_assert_type(str))

    @classmethod
    def from_api_response(cls, resp: Any) -> Iterable['HassStateChange']:
        """Returns a list of `HassStateChanges` parsed from an home assistant api response."""
        return [
            cls(
                friendly_name=item.get('attributes', {}).get('friendly_name', ''),
                entity_id=item.get('entity_id', ''),
                state=item.get('state', 'unknown')
            )
            for item in resp
        ]


SlackTextPayload = str

SlackAttachmentsPayload = List[Dict[str, Any]]

SlackBlocksPayload = List[Dict[str, Any]]


@attr.s
class SlackMessage:
    """A submittable slack message."""
    text: Optional[SlackTextPayload] = attr.ib(
        validator=attrs_assert_type(Optional[SlackTextPayload]),
        default=None
    )
    attachments: Optional[SlackAttachmentsPayload] = attr.ib(
        validator=attrs_assert_type(Optional[SlackAttachmentsPayload]),
        default=None
    )
    blocks: Optional[SlackBlocksPayload] = attr.ib(
        validator=attrs_assert_type(Optional[SlackBlocksPayload]),
        default=None
    )

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> 'SlackMessage':
        """Instantiates a slack message from a dictionary that has contain either the
        text, attachments or blocks key. Or any valid combination of them. See
        the slack online documentation for `chat.postMessage`."""
        text = dct.get('text', None)
        attachments = dct.get('attachments', None)
        blocks = dct.get('blocks', None)
        return cls(text=text, attachments=attachments, blocks=blocks)


@attr.s
class SlackMessageTemplate:
    """Template to render a submittable slack message."""
    template: Any = attr.ib()
    engine: str = attr.ib(default='json')

    @classmethod
    def from_json(cls, json_file: str) -> 'SlackMessageTemplate':
        """Loads the template from a json file and instantiates an instance."""
        with open(json_file, 'r') as fp:
            return cls(template=json.load(fp), engine='json')

    @classmethod
    def from_mako(cls, template_file: str) -> 'SlackMessageTemplate':
        """Loads the mako template from a file and instantiatees an instance."""
        tpl = Template(filename=template_file)
        return cls(template=tpl, engine='mako')

    @classmethod
    def from_file(cls, file_path: str) -> 'SlackMessageTemplate':
        """Loads the templatee from a file and instantiates an instance using the correct
        factory method."""
        ext_mapping = {
            '.json': cls.from_json,
            '.mako': cls.from_mako,
            '.tpl': cls.from_mako
        }
        _, ext = os.path.splitext(file_path)
        factory = ext_mapping.get(ext)
        if not factory:
            raise NotImplementedError(f"Template extension '{ext}' is not supported")

        return factory(file_path)

    def _render_json(self, **context: Any) -> SlackMessage:
        rendered = interpolate_complex(self.template, **context)
        if not isinstance(rendered, dict):
            raise RuntimeError(f"Rendered template needs to be a dict, but is {type(rendered)}")

        return SlackMessage.from_dict(rendered)

    def _render_mako(self, **context: Any) -> SlackMessage:
        rendered = self.template.render(**context)
        json_ = json.loads(rendered)
        if not isinstance(json_, dict):
            raise RuntimeError(f"Rendered template needs to be a dict, but is {type(rendered)}")
        return SlackMessage.from_dict(json_)

    def render(self, **context: Any) -> SlackMessage:
        """Renders out of this `SlackMessageTemplate` a submittable `SlackMessage`."""
        mapping = {
            'json': self._render_json,
            'mako': self._render_mako
        }
        renderer = mapping.get(self.engine)
        if not renderer:
            raise NotImplementedError(f"The template engine '{self.engine}' is not supported.")
        return renderer(**context)
