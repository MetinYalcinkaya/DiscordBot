from datetime import datetime
from unittest.mock import MagicMock

import discord
import pytest
from sqlalchemy import exc

from db.connect import Session
from db.models import User, User_Stock
from db.utils import add_user, get_user


@pytest.fixture
def mock_discord_user():
    user = MagicMock(spec=discord.User)
    user.id = 12345
    user.name = "TestUser"
    return user


@pytest.fixture
def sample_user_stock(mock_discord_user):
    return User_Stock(
        user_id=mock_discord_user.id,
        stock_url="https://test.com/product",
        stock_name="Test Product",
        stock_status=1,
        date_added=datetime.now(),
        last_checked=datetime.now(),
        check_interval=3,
        price="$99.99",
    )


def test_add_user(test_db, mock_discord_user):
    db_user = add_user(mock_discord_user)
    assert db_user.user_id == mock_discord_user.id
    assert db_user.username == mock_discord_user.name

    # Query database directly to verify
    result = test_db.query(User).filter(User.user_id == mock_discord_user.id).first()
    assert result is not None
    assert result.username == mock_discord_user.name


def test_add_duplicate_user(test_db, mock_discord_user):
    add_user(mock_discord_user)
    with pytest.raises(Exception):
        add_user(mock_discord_user)


def test_get_user(test_db, mock_discord_user):
    test_db.add(
        User(
            user_id=mock_discord_user.id,
            username=mock_discord_user.name,
            join_date=datetime.now(),
        )
    )
    test_db.commit()
    result = get_user(mock_discord_user)
    assert result is not None
    assert result.user_id == mock_discord_user.id
    assert result.username == mock_discord_user.name


# test_db is necessary to be a parameter here
# pyright: reportUnusedParameter = false
def test_get_nonexitent_user(test_db, mock_discord_user):
    result = get_user(mock_discord_user)
    assert result is None


# Database CRUD testing
def test_user_stock_create(test_db, sample_user_stock):
    test_db.add(sample_user_stock)
    test_db.commit()

    result = (
        test_db.query(User_Stock).filter_by(user_id=sample_user_stock.user_id).first()
    )
    assert result is not None
    assert result.stock_name == sample_user_stock.stock_name


def test_user_stock_read(test_db, sample_user_stock):
    test_db.add(sample_user_stock)
    test_db.commit()
    result = (
        test_db.query(User_Stock)
        .filter(
            User_Stock.user_id == sample_user_stock.user_id,
            User_Stock.stock_url == sample_user_stock.stock_url,
        )
        .first()
    )
    assert result is not None
    assert result.stock_name == sample_user_stock.stock_name
    assert result.stock_url == sample_user_stock.stock_url


def test_user_stock_update(test_db, sample_user_stock):
    test_db.add(sample_user_stock)
    test_db.commit()

    sample_user_stock.stock_status = 0
    test_db.commit()
    test_db.refresh(sample_user_stock)
    assert sample_user_stock.stock_status == 0


def test_user_stock_delete(test_db, sample_user_stock):
    test_db.add(sample_user_stock)
    test_db.commit()
    test_db.refresh(sample_user_stock)
    test_db.delete(sample_user_stock)

    deleted_check = (
        test_db.query(User_Stock)
        .filter(
            User_Stock.user_id == sample_user_stock.user_id,
            User_Stock.stock_url == sample_user_stock.stock_url,
        )
        .first()
    )

    assert deleted_check is None


def test_transaction_rollback(test_db, mock_discord_user):
    try:
        with test_db.begin():
            test_db.add(
                User(user_id=mock_discord_user.id, username=mock_discord_user.name)
            )
            raise Exception("Simulated error")
    except Exception as _:
        pass
    result = test_db.query(User).filter(User.user_id == mock_discord_user.id).first()
    assert result is None
