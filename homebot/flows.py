"""Contains base code for flow items and the orchestrator itself."""
from typing import Iterable

import attr

from homebot import actions as act
from homebot.formatter import Formatter
from homebot.processors import Processor
from homebot.utils import make_list as mklist
from homebot.validator import (
    attrs_assert_type, attrs_assert_iterable
)


@attr.s
class ErrorFlow:
    """The error flow is called when some exceptions arise or the incoming message
    cannot be handled for some reason."""
    formatters: Iterable[Formatter] = attr.ib(
        converter=mklist,
        validator=attrs_assert_iterable(Formatter)
    )
    actions: Iterable[act.Action] = attr.ib(
        converter=mklist,
        validator=attrs_assert_iterable(act.Action),
    )
    unknown_command_message: str = attr.ib(
        default="No processor is able to handle the message: {message.text}",
        validator=attrs_assert_type(str)
    )
    error_message: str = attr.ib(
        default="Processing of '{message.text} failed: {error_message}'",
        validator=attrs_assert_type(str)
    )


@attr.s
class ActionFlow:
    """Single flow item. The building block of a flow are the following components:
    * processor: Processes the incoming message from the listener.
    * formatters: 0..n formatters to do some formatting to the output of the processor.
    * actions: 1..n actions to perform."""
    processor: Processor = attr.ib(
        validator=attrs_assert_type(Processor)
    )
    formatters: Iterable[Formatter] = attr.ib(
        converter=mklist,
        validator=attrs_assert_iterable(Formatter)
    )
    actions: Iterable[act.Action] = attr.ib(
        converter=mklist,
        validator=attrs_assert_iterable(act.Action),
    )


# The default error flow when no flow was customized for handling errors
DEFAULT_ERROR_FLOW = ErrorFlow(formatters=[], actions=[act.Console()])
