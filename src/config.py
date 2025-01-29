import os

import dotenv

_ = dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_DIR = os.getenv("DB_DIR")
MY_USER_ID = int(os.getenv("MY_USER_ID"))
MY_GUILD_ID = int(os.getenv("MY_GUILD_ID"))
