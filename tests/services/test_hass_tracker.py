import asyncio
from unittest import mock

import pytest

from homebot.services import LocationResolutionError
from homebot.services.hass import HassEntity, PersonTracker


@pytest.yield_fixture(scope='function')
@mock.patch("homebot.processors.hass.HassApi")
def dut(mock_api):
    return PersonTracker(api=mock_api)


@pytest.mark.asyncio
async def test_is_home(dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result([
        HassEntity(domain='person', entity_name='xyz', state='home', unit_of_measurement='', friendly_name='',
                   device_class=None),
    ])
    mapi.states.return_value = f

    assert await dut.is_home('xyz')


@pytest.mark.asyncio
async def test_is_away(dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result([
        HassEntity(domain='person', entity_name='xyz', state='home', unit_of_measurement='', friendly_name='',
                   device_class=None),
    ])
    mapi.states.return_value = f

    assert not await dut.is_away('xyz')


@pytest.mark.asyncio
async def test_no_result(dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result([])
    mapi.states.return_value = f

    with pytest.raises(LocationResolutionError, match="Failed to find the person 'person.unknown in home assistant."):
        assert await dut.is_home('unknown')
    with pytest.raises(LocationResolutionError, match="Failed to find the person 'person.unknown in home assistant."):
        assert not await dut.is_away('unknown')


@pytest.mark.asyncio
async def test_multiple_api_results(dut):
    mapi = dut.api
    f = asyncio.Future()
    f.set_result([
        HassEntity(domain='person', entity_name='xyz', state='home', unit_of_measurement='', friendly_name='',
                   device_class=None),
        HassEntity(domain='person', entity_name='xyz2', state='away', unit_of_measurement='', friendly_name='',
                   device_class=None),
    ])
    mapi.states.return_value = f

    assert not await dut.is_away('xyz')
    assert await dut.is_home('unknown')
