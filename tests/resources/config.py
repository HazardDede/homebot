from homebot import Orchestrator, Flow
from homebot.actions import Console
from tests.conftest import PingListener, DoubleFormatter, PingProcessor


orchestra = Orchestrator(
    listener=PingListener(),
    flows=[Flow(
        processor=PingProcessor(),
        formatters=[DoubleFormatter()],
        actions=[Console()]
    )]
)
