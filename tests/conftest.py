import pytest

from homebot.models import Message, Context, Payload


@pytest.yield_fixture(scope='function')
def dummy_message():
    return Message(
        text="This is the text",
        origin='#general',
        origin_user='the_user',
        direct_mention=True
    )


@pytest.yield_fixture(scope='function')
def dummy_context():
    return Context(
        original_payload=Payload()
    )
