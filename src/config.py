import os

import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_DIR = os.getenv("DB_DIR")
