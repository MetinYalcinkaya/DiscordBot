from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, Unicode, create_engine
from sqlalchemy.orm import declarative_base

from config import DB_DIR

engine = create_engine(str(DB_DIR))
Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = "USER"
    user_id = Column(Unicode, primary_key=True)
    username = Column(Unicode, nullable=False)
    join_date = Column(DateTime, default=datetime.today())

    def __repr__(self) -> str:
        return (
            f"ID: {self.user_id} Username: {self.username} Join Date: {self.join_date}"
        )


class User_Stock(Base):
    __tablename__ = "USER_STOCK"
    user_id = Column(Unicode, primary_key=True)
    stock_url = Column(Unicode, primary_key=True)
    stock_name = Column(Unicode, nullable=False)
    stock_status = Column(Integer, nullable=False)
    date_added = Column(DateTime)
    last_checked = Column(DateTime)
    check_interval = Column(Integer, default=300)  # Default 5 mins

    def __repr__(self) -> str:
        return f"ID: {self.user_id} URL: {self.stock_url} Name: {self.stock_name} Status: {self.stock_status} Date Added: {self.date_added} Last Checked: {self.last_checked} Interval: {self.check_interval}"
