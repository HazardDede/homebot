"""Contains base code for flow items and the orcestrator itself."""

from typing import Iterable

import attr

from homebot.actions import Action
from homebot.formatter import Formatter
from homebot.models import Message
from homebot.listener import Listener
from homebot.processors import Processor


@attr.s
class Flow:
    """Single flow item. The building block of a flow are the following components:
    * processor: Processes the incoming message from the listener.
    * formatters: 0..n formatters to do some formatting to the output of the processor.
    * actions: 1..n actions to perform."""
    # TODO: Check and convert
    processor: Processor = attr.ib()
    formatters: Iterable[Formatter] = attr.ib()
    actions: Iterable[Action] = attr.ib()


class Orchestrator:
    """Orchestrates multiple flows and one listener into a runnable application."""

    def __init__(self, listener: Listener, handlers: Iterable[Flow]):
        self.listener = listener
        # TODO: Check for at least one listener and correct type
        self._flows = handlers
        # TODO: Check for at least one flow and correct types
        for handler in self._flows:
            handler.processor.orchestrator = self

    def _handle(self, message: Message) -> None:
        """Kicks of the flow for one message. This is the callback for the listener."""
        for flow in self._flows:
            if flow.processor.can_process(message.clone()):
                payload = flow.processor(message.clone())
                for formatter in flow.formatters:
                    payload = formatter(payload)
                for action in flow.actions:
                    action(message.clone(), payload)

    def run(self) -> None:
        """Run the application. Will start the listener and kick of the flow on incoming
        messages."""
        self.listener.callback = self._handle
        self.listener.start()
