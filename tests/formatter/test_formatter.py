import pytest

from homebot import Formatter


@pytest.mark.asyncio
async def test_formatter_coworking():
    dut = Formatter(any='kw', args='allowed')
    payload = dict(will='be', returned='as is')
    assert await dut(payload) is payload


def test_formatter_import():
    import homebot.formatter as fmt
    assert fmt.Formatter is not None
