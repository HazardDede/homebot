import os

from homebot import Flow, Orchestrator
from homebot import listener
from homebot import processors
from homebot import formatter as fmt
from homebot import actions
from homebot import services


SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
if not SLACK_TOKEN:
    raise RuntimeError("You have to set SLACK_TOKEN as an environment variable.")

SLACK_BOT_ID = os.environ.get('SLACK_BOT_ID')
if not SLACK_BOT_ID:
    raise RuntimeError("You have to set SLACK_BOT_ID as an environment variable.")


listener = listener.slack.DirectMention(token=SLACK_TOKEN, bot_id=SLACK_BOT_ID)
flows = [
    Flow(
        processor=processors.Version(),
        formatters=[
            fmt.StringFormat("Version of homebot is: `{payload}`"),
        ],
        actions=[actions.slack.SendMessage(token=SLACK_TOKEN)]
    ),
    Flow(
        processor=processors.Help(),
        formatters=[],
        actions=[actions.slack.SendMessage(token=SLACK_TOKEN)]
    ),
    Flow(
        processor=processors.traffic.Traffic(services.traffic.DeutscheBahn()),
        formatters=[fmt.traffic.PlainText(), fmt.slack.Codify()],
        actions=[actions.slack.SendMessage(token=SLACK_TOKEN)]
    )
]
orchester = Orchestrator(listener, flows)
