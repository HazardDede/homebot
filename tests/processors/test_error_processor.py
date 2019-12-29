import pytest

from homebot.models import Payload, ErrorPayload, UnknownCommandPayload
from homebot.processors import ErrorProcessor


@pytest.mark.asyncio
async def test_can_process(message):
    dut = ErrorProcessor()
    assert not await dut.can_process(Payload())
    assert not await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandPayload(command="foo"))
    assert await dut.can_process(ErrorPayload(error_message="blub", trace="bla"))


@pytest.mark.asyncio
async def test_call(ctx):
    dut = ErrorProcessor()
    payload = ErrorPayload(error_message="foo", trace="bar")
    assert await dut(ctx, payload) is payload


def test_import():
    import homebot.processors as proc
    assert proc.ErrorProcessor is not None
