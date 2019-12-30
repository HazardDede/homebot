import asyncio
from unittest import mock

import pytest

from homebot.models import Payload, ErrorPayload, UnknownCommandPayload, HelpEntry, HassStateChange
from homebot.processors.hass import OnOffSwitch

VALID_MESSAGE_TEXT = "switch on domain.switch_entity"
API_RESPONSE = [
    {
        'attributes': {'friendly_name': 'Light', 'supported_features': 0},
        'context': {'id': '61f2037188344d5d9e4321b0aa7ed7e8', 'parent_id': None, 'user_id': None},
        'entity_id': 'light.light_dummy', 'last_changed': '2019-12-30T06:01:08.600274+00:00',
        'last_updated': '2019-12-30T06:01:08.600274+00:00', 'state': 'on'
    },
    {
        'attributes': {'auto': True, 'entity_id': ['light.light_dummy'], 'friendly_name': 'all lights', 'hidden': True,
                       'order': 1},
        'context': {'id': '807685811798414bbfb4383e7a0454d0', 'parent_id': None, 'user_id': None},
        'entity_id': 'group.all_lights', 'last_changed': '2019-12-30T06:01:08.601251+00:00',
        'last_updated': '2019-12-30T06:01:08.601251+00:00', 'state': 'on'
    }
]

@pytest.yield_fixture(scope='function')
@mock.patch("homebot.processors.hass.HassApi")
def dut(mock_api):
    return OnOffSwitch(base_url='http://unknown:8123', token='mytoken')


@pytest.mark.asyncio
async def test_can_process(message, dut):
    assert not await dut.can_process(Payload())
    assert not await dut.can_process(message)
    message.text = "  help   "
    assert not await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandPayload(command="foo"))
    assert not await dut.can_process(ErrorPayload(error_message="blub", trace="bla"))

    message.text = "  switch   on   domain.switch_entity   "
    assert await dut.can_process(message)

    message.text = "  switch   off   domain.switch_entity   "
    assert await dut.can_process(message)


@pytest.mark.asyncio
async def test_call(ctx, message, dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result(API_RESPONSE)
    mapi.call.return_value = f

    message.text = 'switch on light.light_dummy'
    res = await dut(ctx, message)

    mapi.call.assert_called_with(
        'services/homeassistant/turn_on',
        method='post',
        data={'entity_id': 'light.light_dummy'}
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
