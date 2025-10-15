from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum, func, Boolean
from datetime import datetime, timedelta, timezone
from enum import Enum as pyEnum

# Base class for models
Base = declarative_base()

# Enum for Loan Status
class LoanStatus(pyEnum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"

class Roles(pyEnum):
    USER="user"
    ADMIN="admin"

# Book Table
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    publication_year = Column(Integer, nullable=False)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    is_deleted = Column(Boolean, default=False)  # Changed to Boolean for clarity

    # Relationship: One book can have many loans
    loans = relationship("Loan", back_populates="book")

# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # <-- add this
    is_deleted = Column(Boolean, default=False)
    role = Column(SAEnum(Roles), default=Roles.USER, nullable=False)

    # Relationship: One user can have many loans
    loans = relationship("Loan", back_populates="user")

    def is_admin(self):
        return self.role == Roles.ADMIN

# Loan Table
class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    borrow_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(weeks=2), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SAEnum(LoanStatus), default=LoanStatus.BORROWED, nullable=False)
    is_deleted = Column(Boolean, default=False)  # Changed to Boolean
    def is_admin(self):
        return self.role == Roles.ADMIN


    # Relationships
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")

# Audit Table
class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True)
    total_users = Column(Integer, nullable=False)
    total_books = Column(Integer, nullable=False)
    total_loans = Column(Integer, nullable=False)
    active_loans = Column(Integer, nullable=False)
    inactive_users = Column(Integer, nullable=False)
    removed_books = Column(Integer, nullable=False)
    audit_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
