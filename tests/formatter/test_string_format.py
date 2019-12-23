from homebot.formatter import StringFormat
from ..utils import CoWorkingFormatter


def test_string_formatter():
    payload = dict(key='value')
    assert StringFormat("Value: {payload['key']}")(payload) == 'Value: value'


def test_string_formatter_import():
    import homebot.formatter as fmt
    assert fmt.StringFormat is not None


def test_string_formatter_coworking():
    class Before(StringFormat, CoWorkingFormatter):
        pass

    class After(CoWorkingFormatter, StringFormat):
        pass

    assert Before(formatting='#{payload}#')('before') == 'S#before#E'
    assert After(formatting='#{payload}#')('after') == '#SafterE#'
