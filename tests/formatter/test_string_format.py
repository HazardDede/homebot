import pytest

from homebot.formatter import StringFormat
from ..utils import CoWorkingFormatter


@pytest.mark.asyncio
async def test_string_formatter():
    payload = dict(key='value')
    assert await StringFormat("Value: {payload['key']}")(payload) == 'Value: value'


def test_string_formatter_import():
    import homebot.formatter as fmt
    assert fmt.StringFormat is not None


@pytest.mark.asyncio
async def test_string_formatter_coworking():
    class Before(StringFormat, CoWorkingFormatter):
        pass

    class After(CoWorkingFormatter, StringFormat):
        pass

    assert await Before(formatting='#{payload}#')('before') == 'S#before#E'
    assert await After(formatting='#{payload}#')('after') == '#SafterE#'
