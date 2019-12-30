import asyncio
from unittest import mock

import pytest

from homebot.actions.slack import SendMessage


@pytest.mark.asyncio
async def test_call_with_str(ctx):
    with mock.patch('homebot.actions.slack.slack.WebClient.chat_postMessage') as post_message:
        f = asyncio.Future()
        f.set_result(None)
        post_message.return_value = f
        dut = SendMessage(token="itdoesntmatter")
        await dut(ctx, "FOO")
        post_message.assert_called_with(channel="channel", text="FOO")


@pytest.mark.asyncio
async def test_call_with_slack_message(ctx):
    with mock.patch('homebot.actions.slack.slack.WebClient.chat_postMessage') as post_message:
        f = asyncio.Future()
        f.set_result(None)
        post_message.return_value = f
        dut = SendMessage(token="itdoesntmatter")
        await dut(ctx, "FOO")
        post_message.assert_called_with(channel="channel", text="FOO")


def test_import():
    import homebot.actions as actions
    assert actions.slack.SendMessage is not None
