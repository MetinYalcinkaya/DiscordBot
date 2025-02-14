import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.connect import Session as ProdSession
from db.models import Base


# Create fixture for in-memory db
@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()

    # def override_get_session():
    #     return session

    original_session = ProdSession
    ProdSession.configure(bind=engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    ProdSession.configure(bind=original_session.kw["bind"])
