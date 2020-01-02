import asyncio
from unittest import mock

import pytest

from homebot.services.hass import HassApi


class Response:
    @property
    def status_code(self):
        return 200

    def json(self):
        return [{"entity": "1"}, {"entity": 2}]


@pytest.mark.asyncio
async def test_call():
    dut = HassApi('https://egal:8123', token='token')
    with mock.patch('httpx.post') as mpost:
        f = asyncio.Future()
        f.set_result(Response())
        mpost.return_value = f
        res = await dut.call('endpoint', method=HassApi.METHOD_POST, data={'entity_id': 'entity'})

        assert res == [{"entity": "1"}, {"entity": 2}]
