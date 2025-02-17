# DiscordBot

A simple Discord bot written in Python, managed with [uv](https://github.com/astral-sh/uv)

## Dependencies

- [Discord.py](https://github.com/Rapptz/discord.py); Discord API interaction
- [BeautifulSoup](https://code.launchpad.net/beautifulsoup); scraping and parsing webpages
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy); SQLite database interaction
- [Playwright](https://github.com/microsoft/playwright-python); headless browser for http requests
- [Dotenv](https://github.com/theskumar/python-dotenv); .env file functionality
- [PyTest](https://github.com/pytest-dev/pytest/): unit testing

## Features

### Stock Checker

Watches user added links of products to see the price and stock status of it. If
the price or stock status changes, it will direct message the user of the
changes.

### RNG

Various random number generated tools, such as coin flips and dice rolls

## Installation

WIP

## TODO

### General

- [ ] Install instructions
  - [ ] Docker?
- [ ] CLI interactivity
- [x] Unit testing
- [x] Logging

### Core

- [x] Traverse cogs dir to load cogs rather than hard coding
- [x] Rewrite ! prefix to use [app_commands/trees](https://discordpy.readthedocs.io/en/stable/interactions/api.html#appcommand)

### Stock Checker

- [x] Update message as stock is checked #17fb574
- [x] Automated checking #07be7c6
- [x] Pricing tracker #fe1e985
- [x] Deleting watched stocks with buttons

### RNG

- [x] Find better name and group together
  - RNG seems to be good
- [x] Coin flip
- [ ] Dice roll
- [ ] Wheel of fortune?
  - Multiple options, removes previous when landed

### Other

## Acknowledgments

[Ghostty Discord Bot](https://github.com/ghostty-org/discord-bot/) - The idea, motivation, and structure of the project started here
