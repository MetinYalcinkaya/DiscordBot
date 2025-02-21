import os
from pathlib import Path

import dotenv

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = Path(os.getenv("DB_PATH", "src/db/main.db")).absolute()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_DIR = f"sqlite:///{DB_PATH}"
MY_USER_ID = int(os.getenv("MY_USER_ID", "0"))
MY_GUILD_ID = int(os.getenv("MY_GUILD_ID", "0"))
