from pydantic import BaseModel, EmailStr
from datetime import date
import datetime
from typing import Optional
import datetime


# -------------------- BOOK SCHEMAS --------------------
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int


class BookCreate(BookBase):
    # available_copies should be set in API, not provided by user
    pass


class Book(BookBase):
    id: int
    available_copies: int

    class Config:
        from_attributes = True


# -------------------- USER SCHEMAS --------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


# -------------------- LOAN SCHEMAS --------------------
class LoanBase(BaseModel):
    book_id: int
    user_id: int
    borrow_date: Optional[datetime.datetime] = None
    due_date: Optional[datetime.datetime] = None
    return_date: Optional[datetime.datetime] = None
    status: Optional[str] = None


class LoanCreate(BaseModel):
    book_id: int
    user_id: int


class Loan(LoanBase):
    id: int
    # Optional: include nested details
    book: Optional[Book] = None
    user: Optional[User] = None

    class Config:
        from_attributes = True


# -------------------- ACTION SCHEMAS --------------------
class BookBorrowRequest(BaseModel):
    user_id: int


class BookReturnRequest(BaseModel):
    loan_id: int
