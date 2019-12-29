import pytest

from homebot.models import Payload, ErrorPayload, UnknownCommandPayload, HelpEntry
from homebot.processors import Help


@pytest.mark.asyncio
async def test_can_process(message):
    dut = Help()
    assert not await dut.can_process(Payload())
    assert not await dut.can_process(message)
    message.text = "  help   "
    assert await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandPayload(command="foo"))
    assert not await dut.can_process(ErrorPayload(error_message="blub", trace="bla"))


@pytest.mark.asyncio
async def test_call(ctx, message, orchestrator):
    dut = Help()
    message.text = '   help   '
    res = await dut(ctx, message)
    assert isinstance(res, list)
    assert isinstance(res[0], HelpEntry)

    dut.orchestrator = orchestrator
    res = await dut(ctx, message)
    assert isinstance(res, list)
    assert isinstance(res[0], HelpEntry)
    assert res[0].command == 'version'


@pytest.mark.asyncio
async def test_help():
    dut = Help()
    help = await dut.help()
    assert isinstance(help, HelpEntry)
    assert help.command == dut.command


def test_import():
    import homebot.processors as proc
    assert proc.Help is not None
