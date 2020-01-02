import pytest

from homebot import Orchestrator, Flow
from homebot.processors import Error, UnknownCommand
from tests.conftest import PingListener, PingProcessor, DoubleFormatter, MemoryAction, ErrorFormatter


@pytest.mark.asyncio
async def test_for_smoke():
    action = MemoryAction()
    dut = Orchestrator(
        listener=PingListener(),
        flows=[
            Flow(processor=PingProcessor(), formatters=[DoubleFormatter()], actions=[action])
        ]
    )
    await dut.run()
    assert action.memory == [
        "pongpong",
        "pongpong",
        "pongpong",
        "pongpong",
        "pongpong"
    ]


@pytest.mark.asyncio
async def test_error_handling():
    action = MemoryAction()
    dut = Orchestrator(
        listener=PingListener(),
        flows=[
            Flow(processor=PingProcessor(), formatters=[ErrorFormatter()], actions=[action]),
            Flow(processor=Error(), formatters=[], actions=[action])
        ]
    )
    await dut.run()
    assert len(action.memory) == 5
    assert all([err.error_message == 'CRASHED ON PURPOSE' for err in action.memory])


@pytest.mark.asyncio
async def test_unknown_command_handling():
    action = MemoryAction()
    dut = Orchestrator(
        listener=PingListener(),
        flows=[
            Flow(processor=UnknownCommand(), formatters=[], actions=[action])
        ]
    )
    await dut.run()
    assert len(action.memory) == 5
    assert all([err.command == 'ping' for err in action.memory])
