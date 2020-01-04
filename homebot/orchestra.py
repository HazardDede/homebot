"""Contains base code for flow items and the orchestrator itself."""
import asyncio
from typing import Iterable, Any, Optional

import attr

from homebot import actions as act
from homebot.flows import Flow
from homebot.formatter import Formatter
from homebot.listener import Listener
from homebot.models import Incoming, Context, UnknownCommandIncoming, ErrorIncoming, MessageIncoming
from homebot.utils import make_list, LogMixin
from homebot.validator import (
    attrs_assert_type,
    attrs_assert_iterable
)


@attr.s
class Orchestrator(LogMixin):
    """Orchestrates multiple flows and one listener into a runnable application."""

    listener: Listener = attr.ib(
        validator=attrs_assert_type(Listener)
    )
    flows: Iterable[Flow] = attr.ib(
        converter=make_list,
        validator=attrs_assert_iterable(Flow),
    )

    def __attrs_post_init__(self) -> None:
        for flw in self.flows:
            flw.processor.orchestrator = self

    async def _call_formatters(
            self, formatters: Iterable[Formatter], ctx: Context, payload: Any
    ) -> Any:
        for formatter in formatters:
            payload = await formatter(ctx.clone(), payload)
        return payload

    async def _call_actions(
            self, actions: Iterable[act.Action], ctx: Context, payload: Any
    ) -> None:
        coros = [action(ctx.clone(), payload) for action in actions]
        await asyncio.gather(*coros)

    async def _handle_error(self, ctx: Context, error_message: Optional[str] = None) -> None:
        if not error_message:
            import sys
            import traceback
            _, bex, _ = sys.exc_info()
            error_message = str(bex)
            trace = traceback.format_exc()
        else:
            trace = "No trace"

        await self._handle_incoming(ErrorIncoming(error_message, trace), ctx)

    async def _handle_unhandled(self, ctx: Context) -> None:
        command = "unknown"
        if isinstance(ctx.incoming, MessageIncoming):
            command = str(ctx.incoming.text)
        await self._handle_incoming(UnknownCommandIncoming(command), ctx)

    async def _handle_incoming(self, incoming: Incoming, ctx: Optional[Context] = None) -> None:
        """Kicks of the flow for one message. This is the callback for the listener."""
        # Context might be set in case of an error or an unknown message that needs to be
        # handled
        if not ctx:
            ctx = Context(incoming=incoming)

        handled = False
        for flow in self.flows:
            try:
                if await flow.processor.can_process(incoming.clone()):
                    handled = True
                    current = incoming.clone()
                    current = await flow.processor(ctx.clone(), current)
                    current = await self._call_formatters(flow.formatters, ctx, current)
                    await self._call_actions(flow.actions, ctx, current)
            except:  # pylint: disable=bare-except
                self.logger.exception("Error caught while processing the payload:\n%s", str(incoming))
                handled = True
                if not isinstance(incoming, ErrorIncoming):
                    await self._handle_error(ctx)
                else:
                    self.logger.warning("While handling the error a new error was caught. Aborting... ")

        if not handled:
            if not isinstance(incoming, UnknownCommandIncoming):
                await self._handle_unhandled(ctx)
            else:
                self.logger.warning(
                    "Incoming '%s' cannot be handled and no "
                    "unknown command processor is configured.",
                    str(ctx.incoming)
                )

    async def run(self) -> None:
        """Run the application. Will start the listener and kick of the flow on incoming
        messages."""
        self.listener.callback = self._handle_incoming
        await self.listener.start()
