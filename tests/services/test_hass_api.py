import asyncio
from unittest import mock

import pytest

from homebot.services.hass import HassApi, HassStateChange, HassEntity

SWITCH_API_RESPONSE = [
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


STATES_API_RESPONSE = [
    {
        'attributes': {'friendly_name': 'Light', 'supported_features': 0},
        'context': {'id': '61e274af29b147968a3a96705d3b5392', 'parent_id': None, 'user_id': None},
        'entity_id': 'light.light_dummy', 'last_changed': '2020-01-10T20:01:07.148376+00:00',
        'last_updated': '2020-01-10T20:01:07.148376+00:00', 'state': 'off'
    },
    {
        'attributes': {'friendly_name': 'Date', 'icon': 'mdi:calendar'},
        'context': {'id': '7f724c5356f5432d824d2a58894f856b', 'parent_id': None, 'user_id': None},
        'entity_id': 'sensor.date', 'last_changed': '2020-01-10T03:28:06.161237+00:00',
        'last_updated': '2020-01-10T03:28:06.161237+00:00', 'state': '2020-01-10'
    }
]


class Response:
    def __init__(self, json_response):
        self.response = json_response

    @property
    def status_code(self):
        return 200

    def json(self):
        return self.response


@pytest.mark.asyncio
async def test_call():
    dut = HassApi('https://egal:8123', token='token')
    with mock.patch('httpx.post') as mpost:
        f = asyncio.Future()
        f.set_result(Response([{"entity": "1"}, {"entity": 2}]))
        mpost.return_value = f
        res = await dut.call('endpoint', method=HassApi.METHOD_POST, data={'entity_id': 'entity'})

        assert res == [{"entity": "1"}, {"entity": 2}]


@pytest.mark.asyncio
async def test_switch_on_off():
    dut = HassApi('https://egal:8123', token='token')
    with mock.patch('httpx.post') as mpost:
        f = asyncio.Future()
        f.set_result(Response(SWITCH_API_RESPONSE))
        mpost.return_value = f
        res = await dut.switch_on_off('light', 'light_dummy', True)

        assert res == [
            HassStateChange(friendly_name='Light', state='on', entity_id='light.light_dummy'),
            HassStateChange(friendly_name='all lights', state='on', entity_id='group.all_lights')
        ]


@pytest.mark.asyncio
async def test_states():
    dut = HassApi('https://egal:8123', token='token')
    with mock.patch('httpx.get') as mpost:
        f = asyncio.Future()
        f.set_result(Response(STATES_API_RESPONSE))
        mpost.return_value = f

        res = await dut.states()
        assert res == [
            HassEntity(domain='light', entity_name='light_dummy', friendly_name='Light', device_class=None, state='off', unit_of_measurement=''),
            HassEntity(domain='sensor', entity_name='date', friendly_name='Date', device_class=None, state='2020-01-10', unit_of_measurement='')
        ]

        res = await dut.states(domain='light')
        assert res == [
            HassEntity(domain='light', entity_name='light_dummy', friendly_name='Light', device_class=None, state='off', unit_of_measurement=''),
        ]

        res = await dut.states(entity_pattern='.*light.*')
        assert res == [
            HassEntity(domain='light', entity_name='light_dummy', friendly_name='Light', device_class=None, state='off', unit_of_measurement=''),
        ]
