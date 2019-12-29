import pytest

from homebot.formatter.slack import Template
from homebot.models import SlackMessageTemplate, SlackMessage


@pytest.mark.asyncio
async def test_formatter(ctx):
    dut = Template(SlackMessageTemplate(template={'text': '{payload}'}, engine='json'))
    res = await dut(ctx, 'Hello World')
    assert isinstance(res, SlackMessage)
    assert res.text == 'Hello World'
    assert not res.blocks
    assert not res.attachments


def test_formatter_import():
    import homebot.formatter as fmt
    assert fmt.slack.Template is not None
