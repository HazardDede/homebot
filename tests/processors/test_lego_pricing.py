import asyncio
import os
from collections import namedtuple
from unittest import mock

import pytest

from homebot.models import Payload, ErrorPayload, UnknownCommandPayload, HelpEntry, LegoPricing
from homebot.processors.lego import Pricing


@pytest.yield_fixture(scope='function')
def response():
    response = namedtuple('Response', ['status', 'content'])
    file_path = os.path.join(os.path.dirname(__file__), '../resources/sites/bwatch/corvette.html')
    with open(file_path, 'r') as fp:
        yield response(200, fp.read())


@pytest.mark.asyncio
async def test_can_process(message):
    dut = Pricing()
    assert not await dut.can_process(Payload())
    assert not await dut.can_process(message)
    assert not await dut.can_process(UnknownCommandPayload(command="foo"))
    assert not await dut.can_process(ErrorPayload(error_message="blub", trace="bla"))

    message.text = "  lego pricing   12345   "
    assert await dut.can_process(message)


@pytest.mark.asyncio
async def test_call(ctx, message, response):
    with mock.patch('homebot.processors.lego.httpx.get') as mock_get:
        f = asyncio.Future()
        f.set_result(response)
        mock_get.return_value = f

        dut = Pricing()
        message.text = 'lego pricing 12345'
        res = await dut(ctx, message)
        assert isinstance(res, LegoPricing)


@pytest.mark.asyncio
async def test_help():
    dut = Pricing()
    help = await dut.help()
    assert isinstance(help, HelpEntry)
    assert help.command == dut.command


def test_import():
    import homebot.processors as proc
    assert proc.lego.Pricing is not None
