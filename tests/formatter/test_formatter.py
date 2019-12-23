from homebot import Formatter


def test_formatter_coworking():
    dut = Formatter(any='kw', args='allowed')
    payload = dict(will='be', returned='as is')
    assert dut(payload) is payload


def test_formatter_import():
    import homebot.formatter as fmt
    assert fmt.Formatter is not None
