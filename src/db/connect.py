import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from config import DB_DIR

logger = logging.getLogger(__name__)

engine = create_engine(str(DB_DIR))

Session = sessionmaker(bind=engine, expire_on_commit=False)


def try_connect() -> None:
    try:
        with engine.connect() as connection:
            _ = connection.execute(text("SELECT 1"))
            logger.info("Database connection established")
    except Exception:
        engine.dispose()
        logger.error("Failed to connect to database")
        raise RuntimeError("Failed to connect to database")


# try_connect()
