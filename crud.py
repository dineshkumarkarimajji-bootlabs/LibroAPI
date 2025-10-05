
from sqlalchemy.orm import Session
from fastapi import HTTPException
import model, schemas
from datetime import datetime,timedelta,timezone

# Create a new book
def create_book(db: Session, book: schemas.BookCreate):
    db_book = model.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        publication_year=book.publication_year,
        total_copies=book.total_copies,
        available_copies=book.total_copies  # Initially, all copies are available
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

# Retrieve a book by ID
def get_book(db: Session, book_id: int):
    return db.query(model.Book).filter(model.Book.id == book_id, model.Book.BookAvl == 0).first()

# Retrieve all books
def get_books(db: Session, skip: int = 0, limit: int = 100):
    return db.query(model.Book).filter(model.Book.BookAvl == 0).offset(skip).limit(limit).all()

# Update a book
def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for var, value in vars(book).items():
        setattr(db_book, var, value) if value else None
        if 'total_copies' in vars(book):  # Ensure available_copies is updated
            db_book.available_copies = db_book.total_copies
    db.commit()
    db.refresh(db_book)
    return db_book

# Soft delete a book
def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.BookAvl = 1  # Mark as deleted
    db.commit()
    return db_book

# create new user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = model.User(
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# get user by id
def get_user(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id, model.User.Membership == 0).first()    

# get all users
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(model.User).filter(model.User.Membership == 0).offset(skip).limit(limit).all()

# Soft delete a user
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.Membership = 1  # Mark as deleted
    db.commit()
    return db_user

#get Loan by id
def get_loan(db: Session, loan_id: int):
    return db.query(model.Loan).filter(model.Loan.id == loan_id, model.Loan.Softdelete == 0).first()    

# get all loans
def get_loans(db: Session, skip: int = 0, limit: int = 10):
    return db.query(model.Loan).filter(model.Loan.Softdelete == 0).offset(skip).limit(limit).all()  
# Create a new loan (borrow a book)
def create_loan(db: Session, loan: schemas.LoanCreate):
    db_book = db.query(model.Book).filter(model.Book.id == loan.book_id, model.Book.BookAvl == 0).first()
    db_user = db.query(model.User).filter(model.User.id == loan.user_id, model.User.Membership == 0).first()

    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found or unavailable")
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    if db_book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No available copies to borrow")

    db_loan = model.Loan(
        book_id=loan.book_id,
        user_id=loan.user_id
    )
    db_book.available_copies -= 1  # Decrease available copies
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

# Return a book
def return_book(db: Session, loan_id: int): 
    db_loan = get_loan(db, loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if db_loan.status == model.LoanStatus.returned:
        raise HTTPException(status_code=400, detail="Book already returned")

    db_book = db.query(model.Book).filter(model.Book.id == db_loan.book_id, model.Book.BookAvl == 0).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    db_loan.return_date = datetime.now(timezone.utc)
    db_loan.status = model.LoanStatus.returned
    db_book.available_copies += 1  # Increase available copies
    db.commit()
    db.refresh(db_loan)
    return db_loan

#get all overdue loans
def get_overdue_loans(db: Session):
    now = datetime.datetime.utcnow()
    return db.query(model.Loan).filter(model.Loan.due_date < now, model.Loan.status == model.LoanStatus.borrowed, model.Loan.Softdelete == 0).all() 

# soft delete a loan
def delete_loan(db: Session, loan_id: int):
    db_loan = get_loan(db, loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    db_loan.Softdelete = 1  # Mark as deleted
    db.commit()
    return db_loan

# Check and update overdue loans
def check_and_update_overdue_loans(db: Session):
    now = datetime.now(timezone.utc)
    overdue_loans = db.query(model.Loan).filter(
        model.Loan.due_date < now,
        model.Loan.status == model.LoanStatus.borrowed,
        model.Loan.Softdelete == 0
    ).all()
    for loan in overdue_loans:
        loan.status = model.LoanStatus.overdue
    db.commit()
    return overdue_loans