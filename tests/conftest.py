import pytest

import homebot.processors as proc
from homebot import Orchestrator, Flow
from homebot.listener import Listener
from homebot.models import Context, Message


class DummyListener(Listener):
    async def start(self) -> None:
        pass


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
    return Message(
        text="",
        origin_user="user",
        origin="channel",
        direct_mention=True
    )


@pytest.yield_fixture(scope='function')
def ctx(message):
    return Context(
        original_payload=message
    )
