# DiscordBot

A simple Discord bot written in Python, managed with [uv](https://github.com/astral-sh/uv)

## Dependencies

- [Discord.py](https://github.com/Rapptz/discord.py); Discord API interaction
- [BeautifulSoup](https://code.launchpad.net/beautifulsoup); Scraping and parsing webpages
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy); SQLite database interaction
- [Playwright](https://github.com/microsoft/playwright-python); Headless browser for http requests
- [Dotenv](https://github.com/theskumar/python-dotenv); .env file functionality
- [Pytest](https://github.com/pytest-dev/pytest/); Unit testing
- [Docker (Optional)](https://docker.com); For easier install

## Features

### Stock Checker

Watches user added links of products to see the price and stock status of it. If
the price or stock status changes, it will direct message the user of the
changes.

### RNG

Various random number generated tools, such as coin flips and dice rolls

## Installation

### Prerequisites

1. A Discord bot token from Discord's [developer portal](https://discordapp.com/developers/applications/)
2. Your Discord Server Guild ID and your Discord User ID
   - Enable Discord's 'Developer Mode' in `Settings > Advanced > Developer Mode`
   - Right click the Server and `Copy Server ID`
   - Left click your profile picture and `Copy User ID`

### Docker

1. Clone this repository

```bash
git clone https://github.com/MetinYalcinkaya/DiscordBot
```

2. Setup `.env` file
   - Use `example.env` as the base
3. Build and run using `docker-compose`

```bash
   docker-compose up -d --build
```

### With UV

1. Install [astral-sh/uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) for your operating system
2. Clone this repository

```bash
git clone https://github.com/MetinYalcinkaya/DiscordBot
```

3. From the root directory of the project, run `uv sync`
4. Setup your `.env` file
   - Use `example.env` as the base
   - Change file name to `.env`
5. Create the database
   `./create.sh`
   or `python src/migrations/create.py`
6. Run the project
   - `./main.sh` or
   - `uv run src/__main__.py`

## Acknowledgments

[Ghostty Discord Bot](https://github.com/ghostty-org/discord-bot/) - The idea, motivation, and structure of the project started here
