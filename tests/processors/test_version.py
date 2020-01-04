import pytest

from homebot import __VERSION__
from homebot.models import Incoming, ErrorIncoming, UnknownCommandIncoming, HelpEntry
from homebot.processors import Version


@pytest.mark.asyncio
async def test_can_process(message):
    dut = Version()
    assert not await dut.can_process(Incoming())
    assert not await dut.can_process(message)
    message.text = "  version   "
    assert await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandIncoming(command="foo"))
    assert not await dut.can_process(ErrorIncoming(error_message="blub", trace="bla"))


@pytest.mark.asyncio
async def test_call(ctx, message):
    dut = Version()
    message.text = '   version   '
    assert await dut(ctx, message) == __VERSION__


@pytest.mark.asyncio
async def test_help():
    dut = Version()
    help = await dut.help()
    assert isinstance(help, HelpEntry)
    assert help.command == dut.command


def test_import():
    import homebot.processors as proc
    assert proc.Version is not None
