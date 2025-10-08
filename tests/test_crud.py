import pytest
from model import Book, User,Loan,LoanStatus

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

def test_add_user(db_session):
    user = User(
        name="Dinesh",
        email="dinesh@gmail.com"
    )
    db_session.add(user)
    db_session.commit()

    fetched_user = db_session.query(User).filter_by(name="Dinesh").first()
    assert fetched_user is not None
    assert fetched_user.email == "dinesh@gmail.com"

def test_update_user(db_session):
    user = User(
        name="test.user",
        email="testuser@gmail.com"
    )
    db_session.add(user)
    db_session.commit()

    # Update
    user.name = "jayanth"
    db_session.commit()

    updated_user = db_session.query(User).filter_by(email="testuser@gmail.com").first()
    assert updated_user.name == "jayanth"

def test_delete_user(db_session):
    user = User(
        name="Delete user",
        email="deleteuser@gmail.com"
    )
    db_session.add(user)
    db_session.commit()

    # Soft delete
    user.Membership = 1
    db_session.commit()

    deleted_user = db_session.query(User).filter_by(name="Delete user").first()
    assert deleted_user.Membership == 1

def test_cerate_loan(db_session):
    loan=Loan(
        book_id= 1,
        user_id= 1
    )
    db_session.add(loan)
    db_session.commit()

    #featch
    created_loan=db_session.query(Loan).first()
    assert created_loan.user_id==1


def test_return_loan(db_session):
    loan = Loan(id=1)
    fetched_loan = db_session.query(Loan).filter_by(id=loan.id).first()
    fetched_loan.status = LoanStatus.returned
    db_session.commit()

    assert fetched_loan is not None
    assert fetched_loan.status == LoanStatus.returned  # ✅ fixed comparison

