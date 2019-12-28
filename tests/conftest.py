import pytest

from homebot.models import Message


@pytest.yield_fixture(scope='function')
def dummy_message():
    return Message(
        text="This is the text",
        origin='#general',
        origin_user='the_user',
        direct_mention=True
    )
