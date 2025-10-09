from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config import engine,get_db
from model import Base
import schemas
from crud import book_crud

router=APIRouter(tags=["Books"])


# Create tables
Base.metadata.create_all(bind=engine)



@router.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        return book_crud.create_book(db=db, book=book)
    except Exception as error:
        return JSONResponse(status_code=400,content=f'eror due to {error}')
        

# Get a book by ID
@router.get("/books/{book_id}")
def read_book(book_id: int, db: Session = Depends(get_db)):
    try:
        db_book = book_crud.get_book(db, book_id=book_id)
        if db_book is None:
            # raise HTTPException(status_code=404, detail="Book not found")
            return JSONResponse(status_code=404, content="Book not found")
        return db_book
    except Exception as e:
        return JSONResponse(status_code=500,content=f'error due to {e}')
    
# Get all books
@router.get("/books/")
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        books = book_crud.get_books(db, skip=skip, limit=limit)
        return books
    except Exception as E:
        return JSONResponse(status_code=500,content=f'error due to {E}')

# Update a book
@router.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        db_book = book_crud.update_book(db, book_id=book_id, book=book)
        if db_book is None:
            # raise HTTPException(status_code=404, detail="Book not found")
            return JSONResponse(status_code=404,content="Book not found")
        return db_book  
    except Exception as e:
        return JSONResponse(status_code=500,content=f'error due to {e}')    

# Soft delete a book
@router.delete("/books/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    try:
        db_book = book_crud.delete_book(db, book_id=book_id)
        if db_book is None:
            return JSONResponse(status_code=404, content="Book not found")
        return db_book
    except Exception as E:
        return JSONResponse(status_code=500,content=f'error due to {E}')