"""Contains base code for flow items and the orcestrator itself."""
import asyncio
from typing import Iterable, cast, Any

import attr

from homebot import actions as act
from homebot.formatter import Formatter
from homebot.listener import Listener
from homebot.models import Message
from homebot.processors import Processor
from homebot.utils import is_iterable_but_no_str, attrs_assert_iterable, make_list, \
    attrs_assert_type


@attr.s
class ErrorFlow:
    """The error flow is called when some exceptions arise or the incoming message
    cannot be handled for some reason."""
    formatters: Iterable[Formatter] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(Formatter)
    )
    actions: Iterable[act.Action] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(act.Action),
    )
    unknown_command_message: str = attr.ib(
        default="No processor is able to handle the message: {message.text}"
    )


@attr.s
class Flow:
    """Single flow item. The building block of a flow are the following components:
    * processor: Processes the incoming message from the listener.
    * formatters: 0..n formatters to do some formatting to the output of the processor.
    * actions: 1..n actions to perform."""
    processor: Processor = attr.ib(
        validator=attrs_assert_type(Processor)
    )
    formatters: Iterable[Formatter] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(Formatter)
    )
    actions: Iterable[act.Action] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(act.Action),
    )


# The default error flow when no flow was customized for handling errors
DEFAULT_ERROR_FLOW = ErrorFlow(formatters=[], actions=[act.Console()])


@attr.s
class Orchestrator:
    """Orchestrates multiple flows and one listener into a runnable application."""

    listener: Listener = attr.ib(
        validator=attrs_assert_type(Listener)
    )
    flows: Iterable[Flow] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(Flow),
    )
    error_flow: ErrorFlow = attr.ib(
        default=DEFAULT_ERROR_FLOW,
        validator=attrs_assert_type(ErrorFlow)
    )

    def __attrs_post_init__(self) -> None:
        for flw in self.flows:
            flw.processor.orchestrator = self

    async def _call_formatters(
            self, formatters: Iterable[Formatter], payload: Any
    ) -> Any:
        for formatter in formatters:
            payload = await formatter(payload)
        return payload

    async def _call_actions(
            self, actions: Iterable[act.Action], message: Message, payload: Any
    ) -> None:
        coros = [action(message.clone(), payload) for action in actions]
        await asyncio.gather(*coros)

    async def _handle(self, message: Message) -> None:
        """Kicks of the flow for one message. This is the callback for the listener."""
        handled = False
        for flow in self.flows:
            if await flow.processor.can_process(message.clone()):
                handled = True
                payload = await flow.processor(message.clone())
                payload = await self._call_formatters(flow.formatters, payload)
                await self._call_actions(flow.actions, message, payload)

        if not handled:
            err_msg = cast(str, eval(f'f{self.error_flow.unknown_command_message!r}'))  # pylint: disable=eval-used
            err_msg = await self._call_formatters(self.error_flow.formatters, err_msg)
            await self._call_actions(self.error_flow.actions, message, err_msg)

    async def run(self) -> None:
        """Run the application. Will start the listener and kick of the flow on incoming
        messages."""
        self.listener.callback = self._handle
        await self.listener.start()
