from homebot import (
    AssetManager,
    Flow,
    Orchestrator,
    actions,
    formatter as fmt,
    listener,
    processors
)

assets = AssetManager()

# Secrets
SLACK_TOKEN = assets.secret('slack_token')
SLACK_BOT_ID = assets.secret('slack_bot_id')

slack_action = actions.slack.SendMessage(token=SLACK_TOKEN)
help_processor = processors.Help()

listener = listener.slack.DirectMention(token=SLACK_TOKEN, bot_id=SLACK_BOT_ID)
flows = [
    Flow(
        processor=processors.Error(),
        formatters=[fmt.StringFormat(
            "Processing of `{ctx.incoming}` failed: `{payload.error_message}`\n"
            "```{payload.trace}```"
        )],
        actions=[slack_action]
    ),
    Flow(
        processor=processors.UnknownCommand(),
        formatters=[fmt.StringFormat(
            f"Command is invalid: `{{payload.command}}`. Try `{help_processor.command}`."
        )],
        actions=[slack_action]
    ),
    Flow(
        processor=processors.Version(),
        formatters=[
            fmt.StringFormat("Homebot version `{payload}` is up and running...")
        ],
        actions=[slack_action]
    ),
    Flow(
        processor=help_processor,
        formatters=[fmt.help.TextTable(), fmt.slack.Codify()],
        actions=[slack_action]
    )
]
orchestra = Orchestrator(listener, flows)
