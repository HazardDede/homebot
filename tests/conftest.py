import asyncio
from typing import Any, Optional

import pytest

import homebot.processors as proc
from homebot import Orchestrator, Flow
from homebot.actions import Action
from homebot.formatter import Formatter
from homebot.listener import Listener
from homebot.models import Context, MessageIncoming, Incoming, HelpEntry
from homebot.processors import Processor


class DummyListener(Listener):
    async def start(self) -> None:
        pass


class PingListener(Listener):
    def __init__(self, intervals=5, interval_time=0.1):
        super().__init__()
        self.stopped = False
        self.intervals = intervals
        self.interval_time = interval_time

    async def start(self) -> None:
        for _ in range(self.intervals):
            msg = MessageIncoming(
                text="ping",
                origin_user="user",
                origin="channel",
                direct_mention=True
            )
            await self._fire_callback(msg)
            await asyncio.sleep(self.interval_time)


class PingProcessor(Processor):
    async def help(self) -> Optional[HelpEntry]:
        return HelpEntry(command="ping", usage="ping", description="")

    async def can_process(self, incoming: Incoming) -> bool:
        if not hasattr(incoming, 'text'):
            return False
        return str(incoming.text).lower() == 'ping'

    async def __call__(self, ctx: Context, payload: Any) -> Any:
        return "pong"


class DoubleFormatter(Formatter):
    async def __call__(self, ctx: Context, payload: Any) -> Any:
        return payload * 2


class ErrorFormatter(Formatter):
    async def __call__(self, ctx: Context, payload: Any) -> Any:
        raise RuntimeError("CRASHED ON PURPOSE")


class MemoryAction(Action):
    def __init__(self):
        self.memory = []

    async def __call__(self, ctx: Context, payload: Any) -> None:
        self.memory.append(payload)


@pytest.yield_fixture(scope='function')
def orchestrator():
    return Orchestrator(
        listener=DummyListener(),
        flows=[
            Flow(processor=proc.Version(), formatters=[], actions=[])
        ]
    )


@pytest.yield_fixture(scope='function')
def message():
    return MessageIncoming(
        text="ping",
        origin_user="user",
        origin="channel",
        direct_mention=True
    )


@pytest.yield_fixture(scope='function')
def ctx(message):
    return Context(
        incoming=message
    )
