from homebot import (
    AssetManager,
    Flow,
    Orchestrator,
    actions,
    formatter as fmt,
    listener,
    processors,
    services
)

assets = AssetManager()

# Secrets
SLACK_TOKEN = assets.secret('slack_token')
HASS_URI = assets.secret('hass_uri')
HASS_TOKEN = assets.secret('hass_token')

# Template path
TPL_LEGO_PRICING = assets.template_path('tpl_lego_pricing.json')
TPL_HASS_STATE = assets.template_path('tpl_hass_state_change.mako')
TPL_TRAFFIC_TRAIN = assets.template_path('tpl_traffic_train.mako')

slack_action = actions.slack.SendMessage(token=SLACK_TOKEN)
help_processor = processors.Help()

listener = listener.slack.DirectMention(token=SLACK_TOKEN)
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
    ),
    Flow(
        processor=processors.traffic.Traffic(services.traffic.DeutscheBahn()),
        formatters=[fmt.slack.Template.from_file(TPL_TRAFFIC_TRAIN)],
        actions=[slack_action]
    ),
    Flow(
        processor=processors.lego.Pricing(),
        formatters=[fmt.slack.Template.from_file(TPL_LEGO_PRICING)],
        actions=[slack_action]
    ),
    Flow(
        processor=processors.hass.OnOffSwitch(
            base_url=HASS_URI,
            token=HASS_TOKEN
        ),
        formatters=[fmt.slack.Template.from_file(TPL_HASS_STATE)],
        actions=[slack_action]
    )
]
orchestra = Orchestrator(listener, flows)
