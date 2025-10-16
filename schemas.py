from pydantic import BaseModel, EmailStr, constr
from typing import Optional
import datetime
from pydantic import ConfigDict
from model import Roles

# -------------------- BOOK SCHEMAS --------------------
class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: int
    total_copies: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available_copies: int

    model_config = ConfigDict(from_attributes=True)  


# -------------------- USER SCHEMAS --------------------
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Roles = Roles.USER

class UserCreate(UserBase):
    password: constr(min_length=6, max_length=72)

class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # ✅ Pydantic v2


# -------------------- AUTH SCHEMAS --------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[Roles] = None
    id: Optional[int] = None


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
    book: Optional[Book] = None
    user: Optional[User] = None

    model_config = ConfigDict(from_attributes=True)  # ✅ Pydantic v2


# -------------------- ACTION SCHEMAS --------------------
class BookBorrowRequest(BaseModel):
    user_id: int

class BookReturnRequest(BaseModel):
    loan_id: int
