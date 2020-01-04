import os

from homebot import (
    AssetManager,
    Flow,
    Orchestrator,
    actions,
    formatter as fmt,
    listener,
    processors
)

# TODO: Secret Management

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
if not SLACK_TOKEN:
    raise RuntimeError("You have to set SLACK_TOKEN as an environment variable.")

SLACK_BOT_ID = os.environ.get('SLACK_BOT_ID')
if not SLACK_BOT_ID:
    raise RuntimeError("You have to set SLACK_BOT_ID as an environment variable.")


assets = AssetManager()

sender = actions.slack.SendMessage(token=SLACK_TOKEN)
help_processor = processors.Help()

listener = listener.slack.DirectMention(token=SLACK_TOKEN, bot_id=SLACK_BOT_ID)
flows = [
    Flow(
        processor=processors.Error(),
        formatters=[fmt.StringFormat(
            "Processing of `{ctx.incoming}` failed: `{payload.error_message}`\n"
            "```{payload.trace}```"
        )],
        actions=[sender]
    ),
    Flow(
        processor=processors.UnknownCommand(),
        formatters=[fmt.StringFormat(
            f"Command is invalid: `{{payload.command}}`. Try `{help_processor.command}`."
        )],
        actions=[sender]
    ),
    Flow(
        processor=processors.Version(),
        formatters=[
            fmt.StringFormat("Homebot version `{payload}` is up and running...")
        ],
        actions=[sender]
    ),
    Flow(
        processor=help_processor,
        formatters=[fmt.help.TextTable(), fmt.slack.Codify()],
        actions=[sender]
    ),
]
orchestra = Orchestrator(listener, flows)
