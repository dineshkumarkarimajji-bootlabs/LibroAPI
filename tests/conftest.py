import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, Book, User, Loan  # adjust import if your model is in another folder

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(engine):
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

