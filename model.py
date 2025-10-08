from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum,func
from datetime import datetime, timedelta, timezone
from enum import Enum as pyEnum

# Base class for models.SQLAlchemy uses it to collect table metadata and mappings.
Base = declarative_base()

# Enum for Loan Status
class LoanStatus(pyEnum):
    borrowed = "borrowed"
    returned = "returned"
    overdue = "overdue"

# Book Table
class Book(Base):
    __tablename__ = "Books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    publication_year = Column(Integer, nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    BookAvl = Column(Integer, default=0)  # 0 = active, 1 = deleted

    # Relationship: One book can have many loans
    loans = relationship("Loan", back_populates="book")

# User Table
class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    Membership = Column(Integer, default=0)  # 0 = active, 1 = deleted

    # Relationship: One user can have many loans
    loans = relationship("Loan", back_populates="user")

# Loan Table
class Loan(Base):
    __tablename__ = "Loan"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("Books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    borrow_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(weeks=2), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)  # nullable=True to allow not-yet-returned books
    status = Column(SAEnum(LoanStatus), default=LoanStatus.borrowed, nullable=False)
    Softdelete = Column(Integer, default=0)  # 0 = active, 1 = deleted

    # Relationships
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True)
    total_users = Column(Integer, nullable=False)
    total_books = Column(Integer, nullable=False)
    total_loans = Column(Integer, nullable=False)
    active_loans = Column(Integer, nullable=False)
    non_active_users = Column(Integer, nullable=False)
    removed_books = Column(Integer, nullable=False)
    audit_date = Column(DateTime(timezone=True), server_default=func.now())