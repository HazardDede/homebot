import pytest

from homebot.formatter.help import TextTable
from homebot.models import HelpEntry


@pytest.mark.asyncio
async def test_formatter(ctx):
    dut = TextTable(usage_width=10, description_width=20)
    res = await dut(ctx, [HelpEntry("custom", "custom usage", "custom descr")])
    assert res == """+---------+--------------+--------------+
| Command | Usage        | Description  |
+---------+--------------+--------------+
| custom  | custom usage | custom descr |
+---------+--------------+--------------+"""


def test_formatter_import():
    import homebot.formatter as fmt
    assert fmt.help.TextTable is not None
