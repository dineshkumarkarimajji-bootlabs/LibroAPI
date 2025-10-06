import pytest
from model import Book

def test_add_book(db_session):
    book = Book(
        title="CRUD Book",
        author="Author C",
        isbn="ISBN789",
        publication_year=2024,
        total_copies=2,
        available_copies=2
    )
    db_session.add(book)
    db_session.commit()

    # Fetch book
    fetched_book = db_session.query(Book).filter_by(isbn="ISBN789").first()
    assert fetched_book is not None
    assert fetched_book.title == "CRUD Book"

def test_update_book(db_session):
    book = Book(
        title="Update Test",
        author="Author D",
        isbn="ISBN000",
        publication_year=2022,
        total_copies=1,
        available_copies=1
    )
    db_session.add(book)
    db_session.commit()

    # Update
    book.title = "Updated Title"
    db_session.commit()

    updated_book = db_session.query(Book).filter_by(isbn="ISBN000").first()
    assert updated_book.title == "Updated Title"

def test_delete_book(db_session):
    book = Book(
        title="Delete Test",
        author="Author E",
        isbn="ISBNDEL",
        publication_year=2021,
        total_copies=1,
        available_copies=1
    )
    db_session.add(book)
    db_session.commit()

    # Soft delete
    book.BookAvl = 1
    db_session.commit()

    deleted_book = db_session.query(Book).filter_by(isbn="ISBNDEL").first()
    assert deleted_book.BookAvl == 1


