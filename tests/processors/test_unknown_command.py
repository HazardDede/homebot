import pytest

from homebot.models import Payload, ErrorPayload, UnknownCommandPayload
from homebot.processors import UnknownCommandProcessor


@pytest.mark.asyncio
async def test_can_process(message):
    dut = UnknownCommandProcessor()
    assert not await dut.can_process(Payload())
    assert not await dut.can_process(message)
    assert await dut.can_process(UnknownCommandPayload(command="foo"))
    assert not await dut.can_process(ErrorPayload(error_message="blub", trace="bla"))


@pytest.mark.asyncio
async def test_call(ctx):
    dut = UnknownCommandProcessor()
    payload = UnknownCommandPayload(command="foo")
    assert await dut(ctx, payload) is payload


def test_import():
    import homebot.processors as proc
    assert proc.UnknownCommandProcessor is not None
