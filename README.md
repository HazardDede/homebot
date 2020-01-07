# homebot

[![Python](https://img.shields.io/badge/Python-3.7-green.svg)](https://www.python.org/)
[![Build Status](https://travis-ci.org/HazardDede/homebot.svg?branch=master)](https://travis-ci.org/HazardDede/pnp)
[![Coverage Status](https://coveralls.io/repos/github/HazardDede/homebot/badge.svg?branch=master)](https://coveralls.io/github/HazardDede/pnp?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


> The smart bot to the rescue to automate tedious tasks around your home

## Installation

```bash
poetry install --dev
```

## Configuring

TBD

## Docker

```bash
docker build -t homebot .
docker run -it --rm \
    -v `pwd`/config:/config \
    -e HASS_URI=${HASS_URI} \
    -e HASS_TOKEN=${HASS_TOKEN} \
    -e SLACK_TOKEN=${SLACK_TOKEN} \
    -e SLACK_BOT_ID=${SLACK_BOT_ID} \
    homebot
```