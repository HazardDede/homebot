import asyncio
from unittest import mock

import pytest

from homebot.models import Incoming, ErrorIncoming, UnknownCommandIncoming, HelpEntry
from homebot.processors.hass import OnOffSwitch, HassStateChange


@pytest.yield_fixture(scope='function')
@mock.patch("homebot.processors.hass.HassApi")
def dut(mock_api):
    return OnOffSwitch(base_url='http://unknown:8123', token='mytoken')


@pytest.mark.asyncio
async def test_can_process(message, dut):
    assert not await dut.can_process(Incoming())
    assert not await dut.can_process(message)
    message.text = "  help   "
    assert not await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandIncoming(command="foo"))
    assert not await dut.can_process(ErrorIncoming(error_message="blub", trace="bla"))

    message.text = "  hass      switch   on   domain.switch_entity   "
    assert await dut.can_process(message)

    message.text = "  hass     switch   off   domain.switch_entity   "
    assert await dut.can_process(message)


@pytest.mark.asyncio
async def test_call(ctx, message, dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result([
        HassStateChange(friendly_name='Light', state='on', entity_id='light.light_dummy'),
        HassStateChange(friendly_name='all lights', state='on', entity_id='group.all_lights')
    ])
    mapi.switch_on_off.return_value = f

    message.text = 'hass switch on light.light_dummy'
    res = await dut(ctx, message)

    mapi.switch_on_off.assert_called_with(
        'light',
        'light_dummy',
        True
    )
    assert res == [
        HassStateChange(friendly_name='Light', state='on', entity_id='light.light_dummy'),
        HassStateChange(friendly_name='all lights', state='on', entity_id='group.all_lights')
    ]


@pytest.mark.asyncio
async def test_help(dut):
    help = await dut.help()
    assert isinstance(help, HelpEntry)
    assert help.command == dut.command


def test_import():
    import homebot.processors as proc
    assert proc.hass.OnOffSwitch is not None
