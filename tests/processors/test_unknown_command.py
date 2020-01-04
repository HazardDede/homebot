import pytest

from homebot.models import Incoming, ErrorIncoming, UnknownCommandIncoming
from homebot.processors import UnknownCommand


@pytest.mark.asyncio
async def test_can_process(message):
    dut = UnknownCommand()
    assert not await dut.can_process(Incoming())
    assert not await dut.can_process(message)
    assert await dut.can_process(UnknownCommandIncoming(command="foo"))
    assert not await dut.can_process(ErrorIncoming(error_message="blub", trace="bla"))


@pytest.mark.asyncio
async def test_call(ctx):
    dut = UnknownCommand()
    payload = UnknownCommandIncoming(command="foo")
    assert await dut(ctx, payload) is payload


def test_import():
    import homebot.processors as proc
    assert proc.UnknownCommand is not None
