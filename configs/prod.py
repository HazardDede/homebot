import os

from homebot import ErrorFlow, Flow, Orchestrator
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


slack_action = actions.slack.SendMessage(token=SLACK_TOKEN)
help_processor = processors.Help()

listener = listener.slack.DirectMention(token=SLACK_TOKEN, bot_id=SLACK_BOT_ID)
flows = [
    Flow(
        processor=processors.Version(),
        formatters=[
            fmt.StringFormat("Version of homebot is: `{payload}`")
        ],
        actions=slack_action
    ),
    Flow(
        processor=help_processor,
        formatters=[fmt.help.TextTable(), fmt.slack.Codify()],
        actions=slack_action
    ),
    Flow(
        processor=processors.traffic.Traffic(services.traffic.DeutscheBahn()),
        formatters=[fmt.traffic.PlainText(), fmt.slack.Codify()],
        actions=slack_action
    )
]
error_flow = ErrorFlow(
    unknown_command_message="Command is invalid: `{}`. Try `{}` for help page.".format(
        "{message.text}", help_processor._command
    ),
    formatters=[],
    actions=[slack_action]
)
orchester = Orchestrator(listener, flows, error_flow=error_flow)
