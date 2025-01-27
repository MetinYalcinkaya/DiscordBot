# DiscordBot

A simple Discord bot written in Python

## Dependencies

- PyCord; Discord API interaction
- BeautifulSoup; scraping and parsing webpages
- SQLAlchemy; SQLite database interaction
- Playwright; headless browser for http requests
- Dotenv; .env file functionality
- Pytest; Unit testing

## Features

### Stock Checker

Stores users website links and checks state to see if the item is in stock. If
the item isn't in stock, it will intermittently (Deciding proper interval;
currently 5 mins/300 seconds) check if the state of it is changed.

## TODO

### General

- [ ] Install instructions
  - [ ] Docker?

### Stock Checker

- [x] Update message as stock is checked #17fb574
- [x] Automated checking #07be7c6
- [x] Pricing tracker #fe1e985
- [ ] Directly check if pre-order instead of saying in stock
  - [ ] Add to enum

### Other

- [ ] Coin flip
- [ ] Dice roll
- [ ] Wheel of fortune?
  - Multiple options, removes previous when landed
