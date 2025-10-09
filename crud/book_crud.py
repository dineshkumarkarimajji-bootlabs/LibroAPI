from sqlalchemy.orm import Session
from fastapi import HTTPException
import model, schemas



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