from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from src.config import DB_DIR

engine = create_engine(str(DB_DIR))

Session = sessionmaker(bind=engine, expire_on_commit=False)


def try_connect() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("Connection established")
    except Exception:
        engine.dispose()
        raise RuntimeError("Failed to connect")


try_connect()
