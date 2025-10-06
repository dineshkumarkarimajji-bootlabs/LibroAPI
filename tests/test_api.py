import pytest
from fastapi.testclient import TestClient
from main import app
from model import Book

client = TestClient(app)

# Override FastAPI dependency to use test session
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    from main import get_db  # make sure you have a get_db() dependency in main.py
    app.dependency_overrides[get_db] = lambda: db_session

def test_create_book_api(db_session):
    new_book = Book(
        title="Test Book",
        author="Author A",
        isbn="ISBN123",
        publication_year=2025,
        total_copies=5,
        available_copies=5
    )
    db_session.add(new_book)
    db_session.commit()

    book_in_db = db_session.query(Book).filter_by(title="Test Book").first()
    assert book_in_db is not None
    assert book_in_db.author == "Author A"

def test_read_books(db_session):
    book = Book(
        title="Another Book",
        author="Author B",
        isbn="ISBN456",
        publication_year=2023,
        total_copies=3,
        available_copies=3
    )
    db_session.add(book)
    db_session.commit()

    response = client.get("/books")  # make sure this endpoint exists in main.py
    assert response.status_code == 200
    books = response.json()
    assert any(b["title"] == "Another Book" for b in books), "Book not found in API response"
