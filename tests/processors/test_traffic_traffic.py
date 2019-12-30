import pytest

from homebot.models import Payload, ErrorPayload, UnknownCommandPayload, HelpEntry, TrafficInfo, TrafficConnection
from homebot.processors import Help
from homebot.processors.traffic import Traffic
from homebot.services import TrafficService


@pytest.yield_fixture(scope='function')
def dut():
    class DummyService(TrafficService):
        async def pull(self, origin: str, destination: str, only_direct: bool = False, offset: int = 0) -> TrafficInfo:
            return TrafficInfo('origin', 'dest', [
                TrafficConnection('12:00', False, '11:00', ['ICE'], 0, '1:00', False, 0, 0)
            ])

    return Traffic(service=DummyService())


@pytest.mark.asyncio
async def test_can_process(dut, message):
    assert not await dut.can_process(Payload())
    assert not await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandPayload(command="foo"))
    assert not await dut.can_process(ErrorPayload(error_message="blub", trace="bla"))

    message.text = "  traffic   origin    to      dest   "
    assert await dut.can_process(message)


@pytest.mark.asyncio
async def test_call(dut, ctx, message):
    message.text = "  traffic   origin    to      dest   "
    res = await dut(ctx, message)
    assert isinstance(res, TrafficInfo)
    assert len(list(res.connections)) == 1


@pytest.mark.asyncio
async def test_help():
    dut = Help()
    help = await dut.help()
    assert isinstance(help, HelpEntry)
    assert help.command == dut.command


def test_import():
    import homebot.processors as proc
    assert proc.traffic.Traffic is not None
