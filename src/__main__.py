from core import bot, config
from db.connect import try_connect

try_connect()
bot.run(config.BOT_TOKEN)
