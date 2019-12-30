import os

from homebot import Flow, Orchestrator
from homebot import actions
from homebot import formatter as fmt
from homebot import listener
from homebot import processors
from homebot import services

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
if not SLACK_TOKEN:
    raise RuntimeError("You have to set SLACK_TOKEN as an environment variable.")

SLACK_BOT_ID = os.environ.get('SLACK_BOT_ID')
if not SLACK_BOT_ID:
    raise RuntimeError("You have to set SLACK_BOT_ID as an environment variable.")

HASS_TOKEN = os.environ.get('HASS_TOKEN')
if not HASS_TOKEN:
    raise RuntimeError("You have to set HASS_TOKEN as an environment variable.")


TPL_LEGO_PRICING = './assets/tpl_lego_pricing.json'
TPL_HASS_STATE = './assets/tpl_hass_state_change.mako'
TPL_TRAFFIC_TRAIN = './assets/tpl_traffic_train.mako'

slack_action = actions.slack.SendMessage(token=SLACK_TOKEN)
help_processor = processors.Help()

listener = listener.slack.DirectMention(token=SLACK_TOKEN, bot_id=SLACK_BOT_ID)
flows = [
    Flow(
        processor=processors.Error(),
        formatters=[fmt.StringFormat(
            "Processing of `{ctx.original_payload}` failed: `{payload.error_message}`\n"
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
            base_url='http://localhost:8123',
            token=HASS_TOKEN
        ),
        formatters=[fmt.slack.Template.from_file(TPL_HASS_STATE)],
        actions=[slack_action]
    )
]
orchestra = Orchestrator(listener, flows)
