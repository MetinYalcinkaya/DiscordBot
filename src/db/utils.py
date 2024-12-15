import discord

from db.connect import Session

from .models import User, User_Stock


def add_user(user: discord.Member) -> User:
    with Session() as session:
        db_user = User(user_id=user.id, username=user.name)
        session.add(db_user)
        session.commit()
        return db_user


def get_user(user: discord.Member) -> User | None:
    with Session() as session:
        return session.query(User).filter(User.user_id == user.id).one_or_none()


def add_stock(user: discord.Member, url):
    with Session() as session:
        db_stock = User_Stock(user_id=user.id, stock_url=url)
        session.add(db_stock)
        session.commit()


def get_stock(user: discord.Member, url) -> User_Stock | None:
    with Session() as session:
        return (
            session.query(User_Stock)
            .filter(User_Stock.user_id == user.id, User_Stock.stock_url == url)
            .one_or_none()
        )
