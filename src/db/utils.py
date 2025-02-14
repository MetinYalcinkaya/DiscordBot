import logging
from datetime import datetime

import discord

from db.connect import Session

from .models import User

logger = logging.getLogger(__name__)


def add_user(user: discord.Member | discord.User) -> User:
    """
    Adds given user to the database
    """
    with Session() as session:
        db_user = User(user_id=user.id, username=user.name, join_date=datetime.now())
        try:
            session.add(db_user)
        except Exception as e:
            logger.error(f"Adding user error, rolling back: {e}")
            session.rollback()
        finally:
            session.commit()
            return db_user


def get_user(user: discord.Member | discord.User) -> User | None:
    with Session() as session:
        return session.query(User).filter(User.user_id == user.id).one_or_none()
