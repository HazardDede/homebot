"""Contains base code for flow items and the orchestrator itself."""
import asyncio
from typing import Iterable, Any, Optional, Union

import attr

from homebot import actions as act
from homebot.flows import ActionFlow, ErrorFlow, DEFAULT_ERROR_FLOW
from homebot.formatter import Formatter
from homebot.listener import Listener
from homebot.models import Message
from homebot.utils import make_list, interpolate
from homebot.validator import (
    attrs_assert_type,
    attrs_assert_iterable
)


@attr.s
class Orchestrator:
    """Orchestrates multiple flows and one listener into a runnable application."""

    listener: Listener = attr.ib(
        validator=attrs_assert_type(Listener)
    )
    flows: Iterable[ActionFlow] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(ActionFlow),
    )
    error_flow: ErrorFlow = attr.ib(
        default=DEFAULT_ERROR_FLOW,
        validator=attrs_assert_type(ErrorFlow)
    )

    def __attrs_post_init__(self) -> None:
        for flw in self.flows:
            flw.processor.orchestrator = self

    async def _call_formatters(
            self, formatters: Iterable[Formatter], message: Message, payload: Any
    ) -> Any:
        for formatter in formatters:
            payload = await formatter(message.clone(), payload)
        return payload

    async def _call_actions(
            self, actions: Iterable[act.Action], message: Message, payload: Any
    ) -> None:
        coros = [action(message.clone(), payload) for action in actions]
        await asyncio.gather(*coros)

    async def _run_flow(self, flow: Union[ErrorFlow, ActionFlow], message: Message, payload: Any) -> None:
        payload = await self._call_formatters(flow.formatters, message, payload)
        await self._call_actions(flow.actions, message, payload)

    async def _handle_error(self, message: Message, error_message: Optional[str] = None) -> None:
        if not error_message:
            import sys
            import traceback
            _, bex, _ = sys.exc_info()
            error_message = str(bex)
            trace = traceback.format_exc()
        else:
            trace = "No trace"

        printable_msg = interpolate(
            self.error_flow.error_message,
            error_message=error_message, trace=trace, message=message
        )
        await self._run_flow(self.error_flow, message, printable_msg)

    async def _handle_unhandled(self, message: Message) -> None:
        printable_message = interpolate(
            self.error_flow.unknown_command_message,
            message=message
        )
        await self._run_flow(self.error_flow, message, printable_message)

    async def _handle_incoming(self, message: Message) -> None:
        """Kicks of the flow for one message. This is the callback for the listener."""
        handled = False
        for flow in self.flows:
            try:
                if await flow.processor.can_process(message.clone()):
                    handled = True
                    payload = await flow.processor(message.clone())
                    await self._run_flow(flow, message, payload)
            except:  # pylint: disable=bare-except
                await self._handle_error(message)

        if not handled:
            await self._handle_unhandled(message)

    async def run(self) -> None:
        """Run the application. Will start the listener and kick of the flow on incoming
        messages."""
        self.listener.callback = self._handle_incoming
        await self.listener.start()
