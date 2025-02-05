from datetime import datetime

from sqlalchemy import DateTime, Integer, Unicode, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from config import DB_DIR

engine = create_engine(str(DB_DIR))
Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = "USER"
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(Unicode, nullable=False)
    join_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.today())

    def __repr__(self) -> str:
        return (
            f"ID: {self.user_id} Username: {self.username} Join Date: {self.join_date}"
        )


class User_Stock(Base):
    __tablename__ = "USER_STOCK"
    user_id: Mapped[int] = mapped_column(Unicode, primary_key=True)
    stock_url: Mapped[str] = mapped_column(Unicode, primary_key=True)
    stock_name: Mapped[str] = mapped_column(Unicode, nullable=False)
    stock_status: Mapped[int] = mapped_column(Integer, nullable=False)
    date_added: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_checked: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    check_interval: Mapped[int] = mapped_column(Integer, default=300)  # Default 5 mins
    price: Mapped[str] = mapped_column(Unicode, nullable=False)

    def __repr__(self) -> str:
        return f"ID: {self.user_id} URL: {self.stock_url} Name: {self.stock_name} Status: {self.stock_status} Date Added: {self.date_added} Last Checked: {self.last_checked} Interval: {self.check_interval} Price: {self.price}"
