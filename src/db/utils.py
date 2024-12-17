import discord

from db.connect import Session

from .models import User


def add_user(user: discord.Member) -> User:
    with Session() as session:
        db_user = User(user_id=user.id, username=user.name)
        session.add(db_user)
        session.commit()
        return db_user


def get_user(user: discord.Member) -> User | None:
    with Session() as session:
        return session.query(User).filter(User.user_id == user.id).one_or_none()
