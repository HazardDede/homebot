# homebot

[![Python](https://img.shields.io/badge/Python-3.7-green.svg)](https://www.python.org/)
[![Build Status](https://travis-ci.org/HazardDede/homebot.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)
[![Coverage Status](https://coveralls.io/repos/github/HazardDede/homebot/badge.svg?branch=master)](https://coveralls.io/github/HazardDede/pnp?branch=master)
[![Docker Hub](https://img.shields.io/badge/docker-hub-green.svg)](https://hub.docker.com/r/hazard/homebot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


> The smart bot to the rescue to automate tedious tasks around your home

## Installation

Installation is easy:

```bash
poetry install --no-dev
# Run a shell in the virtualenv
poetry shell
```

## Getting started

Any `homebot` configuration is real python code which can be linted, tested, highlighted and many more
like any other python code. In comparison to other configuration formats - for example yaml configurations -  
it is easy to spot errors cause your IDE (like PyCharm) will highlight errors.

By now homebot only supports `slack` to listen for messages from users. 
You need to setup a bot account in slack (documentation will follow).

Create a python file (I will call it `run.py`) and paste the following content into it:

```python
from homebot import (
    AssetManager,
    Flow,
    Orchestrator,
    actions,
    formatter as fmt,
    listener,
    processors
)

assets = AssetManager()  # Helper to retrieve secrets and assets

# Secrets
SLACK_TOKEN = assets.secret('slack_token')  # export SLACK_TOKEN=<your_token>
SLACK_BOT_ID = assets.secret('slack_bot_id')    # export SLACK_BOT_ID=<your_bot_id>

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
```

This setups a bot that is able to handle errors (`processors.Error`), unknown commands from the user (`processors.UnknownCommand()`),
provide a help / usage message to slack channel (`processors.Help`) and can show the current version (`processors.Version`).

After that you can call

```bash
# If you did not name it run.py change it to suit your needs!
python homebot run run.py
```

to run `homebot`.

Go to your slack workspace where the bot is installed, invite the bot to a channel and try out
the different commands:

```
# Remark: <botname> is the name of your bot. Replace to suit your needs
# Show the help / usage page of your bot
@<botname> help
# Show the current version of homebot
@<botname> version
```

## Building Blocks

TBD

## Docker

TBD

```bash
docker run -it --rm \
    -v `pwd`/configs/complex:/config \
    -e HASS_URI=${HASS_URI} \
    -e HASS_TOKEN=${HASS_TOKEN} \
    -e SLACK_TOKEN=${SLACK_TOKEN} \
    -e SLACK_BOT_ID=${SLACK_BOT_ID} \
    hazard/homebot:0.1.1
```