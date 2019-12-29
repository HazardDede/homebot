import pytest

from homebot.formatter.slack import Codify
from homebot.models import SlackMessage


@pytest.mark.asyncio
async def test_formatter(ctx):
    dut = Codify()
    assert await dut(ctx, "String") == "```String```"
    res = await dut(ctx, SlackMessage(text="String"))
    assert isinstance(res, SlackMessage)
    assert res.text == "```String```"


def test_formatter_import():
    import homebot.formatter as fmt
    assert fmt.slack.Codify is not None
