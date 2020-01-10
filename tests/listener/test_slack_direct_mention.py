import asyncio
from unittest import mock
from unittest.mock import MagicMock

import pytest

from homebot.listener.base import ListenerError
from homebot.listener.slack import DirectMention


class CallbackAssert:
    def __init__(self, message, channel, user):
        self.message = message
        self.channel = channel
        self.user = user
        self.called = False

    async def __call__(self, message):
        print(message)
        self.called = True
        assert message.text == self.message
        assert message.origin == self.channel
        assert message.origin_user == self.user


@pytest.mark.asyncio
async def test_start():
    with mock.patch('homebot.listener.slack.slack.RTMClient') as rtm_mock:
        f = asyncio.Future()
        f.set_result(None)
        rtm_mock.return_value = MagicMock()
        rtm_mock.return_value.start.return_value = f

        dut = DirectMention('token')
        await dut.start()

        rtm_mock.return_value.start.assert_called_once()
        rtm_mock.return_value.on.assert_called_once()


@pytest.mark.asyncio
async def test_on_message_with_direct_mention():
    with mock.patch('homebot.listener.slack.slack.WebClient') as slack_mock:
        f = asyncio.Future()
        f.set_result({'ok': True, 'user_id': 'bot_id'})
        slack_mock.return_value = MagicMock()
        slack_mock.return_value.auth_test.return_value = f

        dut = DirectMention('token')
        cb = CallbackAssert('ping', 'chnl', 'somebody')
        dut.callback = cb
        await dut._on_message({'text': '<@bot_id> ping', 'channel': 'chnl', 'user': 'somebody'})
        await asyncio.sleep(0.05)
        assert cb.called


@pytest.mark.asyncio
async def test_on_message_with_no_mention():
    with mock.patch('homebot.listener.slack.slack.WebClient') as slack_mock:
        f = asyncio.Future()
        f.set_result({'ok': True, 'user_id': 'bot_id'})
        slack_mock.return_value = MagicMock()
        slack_mock.return_value.auth_test.return_value = f

        dut = DirectMention('token')
        cb = CallbackAssert('ping', 'chnl', 'somebody')
        dut.callback = cb
        await dut._on_message({'text': 'ping', 'channel': 'chnl', 'user': 'somebody'})
        await asyncio.sleep(0.05)
        assert not cb.called


@pytest.mark.asyncio
async def test_bot_user_id_slack_ok():
    with mock.patch('homebot.listener.slack.slack.WebClient') as slack_mock:
        f = asyncio.Future()
        f.set_result({'ok': True, 'user_id': 'the_bot_id'})
        slack_mock.return_value = MagicMock()
        slack_mock.return_value.auth_test.return_value = f

        dut = DirectMention('token')
        assert await dut.bot_user_id == 'the_bot_id'


@pytest.mark.asyncio
async def test_bot_user_id_slack_fail():
    with mock.patch('homebot.listener.slack.slack.WebClient') as slack_mock:
        f = asyncio.Future()
        f.set_result({'ok': False, 'user_id': 'the_bot_id'})
        slack_mock.return_value = MagicMock()
        slack_mock.return_value.auth_test.return_value = f

        dut = DirectMention('token')
        with pytest.raises(ListenerError, match="Failed to retrieve the slack user_id of the bot."):
            await dut.bot_user_id
