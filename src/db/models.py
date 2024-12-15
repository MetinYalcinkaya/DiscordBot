from sqlalchemy import Column, Unicode, create_engine
from sqlalchemy.orm import declarative_base

from config import DB_DIR

engine = create_engine(str(DB_DIR))
Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = "USER"
    user_id = Column(Unicode, primary_key=True)
    username = Column(Unicode, nullable=False)

    def __repr__(self) -> str:
        return f"user_id={self.user_id}|username={self.username}"

    def __str__(self) -> str:
        return f"ID: {self.user_id} Username: {self.username}"


class User_Stock(Base):
    __tablename__ = "USER_STOCK"
    user_id = Column(Unicode, primary_key=True)
    stock_url = Column(Unicode, primary_key=True)
    stock_name = Column(Unicode, nullable=False)

    def __repr__(self) -> str:
        return f"user_id={self.user_id}|stock_url={self.stock_url}|stock_name={self.stock_name}"

    def __str__(self) -> str:
        return f"ID: {self.user_id} URL: {self.stock_url} Name: {self.stock_name}"
