import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base
from fastapi.testclient import TestClient
from main import app
from config import get_db

# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///memory.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

# Dependency override for FastAPI
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Fixture for API tests
@pytest.fixture(scope="function")
def client():
    client_=TestClient(app)
    return client_

# Fixture for direct DB access (CRUD tests)
@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
