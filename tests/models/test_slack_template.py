import os

from homebot.models import SlackMessageTemplate, SlackMessage


def test_from_json():
    json_path = os.path.join(os.path.dirname(__file__), '../resources/templates/tpl.json')
    dut = SlackMessageTemplate.from_json(json_path)
    assert dut.engine == 'json'
    res = dut.render(payload="PAYLOAD")

    assert isinstance(res, SlackMessage)
    assert res.text == '### PAYLOAD ###'
    assert not res.blocks
    assert not res.attachments


def test_from_mako():
    mako_path = os.path.join(os.path.dirname(__file__), '../resources/templates/tpl.mako')
    dut = SlackMessageTemplate.from_mako(mako_path)
    assert dut.engine == 'mako'
    res = dut.render(payload="PAYLOAD")

    assert isinstance(res, SlackMessage)
    assert res.text == '### PAYLOAD ###'
    assert not res.blocks
    assert not res.attachments


def test_from_file():
    json_path = os.path.join(os.path.dirname(__file__), '../resources/templates/tpl.json')
    mako_path = os.path.join(os.path.dirname(__file__), '../resources/templates/tpl.mako')

    dut = SlackMessageTemplate.from_file(json_path)
    assert dut.engine == 'json'
    res = dut.render(payload="PAYLOAD")
    assert res.text == '### PAYLOAD ###'

    dut = SlackMessageTemplate.from_file(mako_path)
    assert dut.engine == 'mako'
    res = dut.render(payload="PAYLOAD")
    assert res.text == '### PAYLOAD ###'
