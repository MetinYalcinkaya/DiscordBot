import discord
import models

from db.connect import Session


def add_user(user: discord.Member) -> models.User:
    with Session() as session:
        db_user = models.User(user_id=user.id, username=user.name)
        session.add(db_user)
        session.commit()
        return db_user


def get_user(user: discord.Member) -> models.User | None:
    with Session() as session:
        return (
            session.query(models.User)
            .filter(models.User.user_id == user.id)
            .one_or_none()
        )
