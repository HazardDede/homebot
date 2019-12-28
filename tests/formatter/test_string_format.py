import pytest

from homebot.formatter import StringFormat


@pytest.mark.asyncio
async def test_string_formatter(dummy_message):
    payload = dict(key='value')
    assert await StringFormat("Value: {payload['key']}")(dummy_message, payload) == 'Value: value'


def test_string_formatter_import():
    import homebot.formatter as fmt
    assert fmt.StringFormat is not None
