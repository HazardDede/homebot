import pytest

from homebot.formatter import StringFormat


@pytest.mark.asyncio
async def test_formatter(ctx):
    payload = dict(key='value')
    assert await StringFormat("Value: {payload['key']}")(ctx, payload) == 'Value: value'


def test_formatter_import():
    import homebot.formatter as fmt
    assert fmt.StringFormat is not None
