import asyncio
from unittest import mock

import pytest

from homebot.models import Incoming, ErrorIncoming, UnknownCommandIncoming, HelpEntry
from homebot.processors.hass import Entities
from homebot.services.hass import HassEntity


@pytest.yield_fixture(scope='function')
@mock.patch("homebot.processors.hass.HassApi")
def dut(mock_api):
    return Entities(base_url='http://unknown:8123', token='mytoken')


@pytest.mark.asyncio
async def test_can_process(message, dut):
    assert not await dut.can_process(Incoming())
    assert not await dut.can_process(message)
    message.text = "  help   "
    assert not await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandIncoming(command="foo"))
    assert not await dut.can_process(ErrorIncoming(error_message="blub", trace="bla"))

    message.text = "  hass      entity   *pattern   "
    assert await dut.can_process(message)

    message.text = "  hass     entity   light.*   "
    assert await dut.can_process(message)


@pytest.mark.asyncio
async def test_call(ctx, message, dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result([
        HassEntity(domain='light', entity_name='dummy', state='on', unit_of_measurement='', friendly_name='Light', device_class=None),
    ])
    mapi.states.return_value = f

    message.text = 'hass entity light.*'
    res = await dut(ctx, message)
    mapi.states.assert_called_with(
        domain='light',
        entity_pattern='*'
    )
    assert res == [
        HassEntity(domain='light', entity_name='dummy', state='on', unit_of_measurement='', friendly_name='Light', device_class=None)
    ]

    message.text = 'hass entity dummy'
    res = await dut(ctx, message)
    mapi.states.assert_called_with(
        domain=None,
        entity_pattern='dummy'
    )
    assert res == [
        HassEntity(domain='light', entity_name='dummy', state='on', unit_of_measurement='', friendly_name='Light', device_class=None)
    ]

    message.text = 'hass entity'
    res = await dut(ctx, message)
    mapi.states.assert_called_with(
        domain=None,
        entity_pattern=None
    )
    assert res == [
        HassEntity(domain='light', entity_name='dummy', state='on', unit_of_measurement='', friendly_name='Light', device_class=None)
    ]


@pytest.mark.asyncio
async def test_help(dut):
    help = await dut.help()
    assert isinstance(help, HelpEntry)
    assert help.command == dut.command


def test_import():
    import homebot.processors as proc
    assert proc.hass.Entities is not None
