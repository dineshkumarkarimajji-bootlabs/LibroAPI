from sqlalchemy.orm import Session
from fastapi import HTTPException
import model, schemas, auth
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError,IntegrityError

# -------------------- BOOK CRUD --------------------
def create_book(db: Session, book: schemas.BookCreate):
    db_book = model.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        publication_year=book.publication_year,
        total_copies=book.total_copies,
        available_copies=book.total_copies
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book(db: Session, book_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(model.Book).filter(model.Book.is_deleted == False)
    if book_id is not None:
        return query.filter(model.Book.id == book_id).first()
    return query.offset(skip).limit(limit).all()


def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    for var, value in vars(book).items():
        setattr(db_book, var, value) if value is not None else None

    if 'total_copies' in vars(book):
        db_book.available_copies = db_book.total_copies

    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.is_deleted = True
    db.commit()
    return db_book

# -------------------- USER CRUD --------------------
def create_user(db: Session, user: schemas.UserCreate):
    # Hash the password
    hashed_password = auth.get_password_hash(user.password)
    db_user = model.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Generate JWT token
    token_data = {"sub": db_user.email, "id": db_user.id, "role": db_user.role.value}
    token = auth.create_access_token(token_data)

    # Return response matching the schemas
    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role.value,
        "access_token": token,
        "token_type": "bearer"
    }



def authenticate_user(db: Session, email: str, password: str):
    user = db.query(model.User).filter(
        model.User.email == email,
        model.User.is_deleted == False
    ).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token_data = {"sub": user.email, "id": user.id, "role": user.role.value}
    token = auth.create_access_token(token_data)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
    }


def get_user(db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 10):
    query = db.query(model.User).filter(model.User.is_deleted == False)
    if user_id is not None:
        return query.filter(model.User.id == user_id).first()
    return query.offset(skip).limit(limit).all()


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.is_deleted = True
    db.commit()
    return db_user

# -------------------- LOAN CRUD --------------------
def get_loan(db: Session, loan_id: Optional[int] = None, skip: int = 0, limit: int = 10):
    query = db.query(model.Loan).filter(model.Loan.is_deleted == False)
    if loan_id is not None:
        return query.filter(model.Loan.id == loan_id).first()
    return query.offset(skip).limit(limit).all()


def create_loan(db: Session, loan: schemas.LoanCreate):
    try:
        db_book = (
            db.query(model.Book)
            .filter(model.Book.id == loan.book_id, model.Book.is_deleted == False)
            .first()
        )
        db_user = (
            db.query(model.User)
            .filter(model.User.id == loan.user_id, model.User.is_deleted == False)
            .first()
        )
        if db_book is None:
            raise HTTPException(status_code=404, detail="Book not found")
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if db_book.available_copies < 1:
            raise HTTPException(status_code=400, detail="No copies available")

        db_loan = model.Loan(
            book_id=loan.book_id,
            user_id=loan.user_id,
            borrow_date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=14),
            status=model.LoanStatus.BORROWED
        )
        db_book.available_copies -= 1
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


def return_book(db: Session, loan_id: int):
    db_loan = db.query(model.Loan).filter(
        model.Loan.id == loan_id,
        model.Loan.is_deleted == False
    ).first()
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    if db_loan.status == model.LoanStatus.RETURNED:
        raise HTTPException(status_code=400, detail="Book already returned")

    db_book = db.query(model.Book).filter(
        model.Book.id == db_loan.book_id,
        model.Book.is_deleted == False
    ).with_for_update().first()

    db_loan.return_date = datetime.now(timezone.utc)
    db_loan.status = model.LoanStatus.RETURNED
    db_book.available_copies += 1

    db.commit()
    db.refresh(db_loan)
    return db_loan


def delete_loan(db: Session, loan_id: int):
    db_loan = get_loan(db, loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    db_loan.is_deleted = True
    db.commit()
    return db_loan


def check_and_update_overdue_loans(db: Session):
    now = datetime.now(timezone.utc)
    overdue_loans = db.query(model.Loan).filter(
        model.Loan.due_date < now,
        model.Loan.status == model.LoanStatus.BORROWED,
        model.Loan.is_deleted == False
    ).all()
    for loan in overdue_loans:
        loan.status = model.LoanStatus.OVERDUE
    db.commit()
    return overdue_loans

# -------------------- AUDIT --------------------
def audit_record(db: Session):
    total_users = db.query(func.count(model.User.id)).scalar()
    total_books = db.query(func.count(model.Book.id)).scalar()
    total_loans = db.query(func.count(model.Loan.id)).scalar()
    active_loans = db.query(func.count(model.Loan.id)).filter(
        model.Loan.status != model.LoanStatus.RETURNED,
        model.Loan.is_deleted == False
    ).scalar()
    inactive_users = db.query(func.count(model.User.id)).filter(
        model.User.is_deleted == True
    ).scalar()
    removed_books = db.query(func.count(model.Book.id)).filter(
        model.Book.is_deleted == True
    ).scalar()

    new_audit = model.Audit(
        total_users=total_users,
        total_books=total_books,
        total_loans=total_loans,
        active_loans=active_loans,
        inactive_users=inactive_users,
        removed_books=removed_books
    )
    db.add(new_audit)
    db.commit()
    db.refresh(new_audit)
    return {
        "message": f"Audit record created successfully with id {new_audit.id}",
        "audit": {
            "total_users": total_users,
            "non_active_users": inactive_users,
            "total_books": total_books,
            "removed_books": removed_books,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "audit_date": new_audit.audit_date
        }
    }
