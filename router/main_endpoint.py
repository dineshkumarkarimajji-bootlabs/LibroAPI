from fastapi import APIRouter,Depends,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config import engine,get_db
from model import Base,Loan
import schemas
from crud import main_crud

router=APIRouter(tags=["Books"])
router2 = APIRouter(tags=['users'])
router3 = APIRouter(tags=["Loans"])
router4=APIRouter(tags=["Audit"])

# Create tables
Base.metadata.create_all(bind=engine)


@router.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        return main_crud.create_book(db=db, book=book)
    except Exception as error:
        return JSONResponse(status_code=400,content=f'eror due to {error}')
        

@router.get("/books/")
def read_books_route(
    book_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    - Fetch a single book if `book_id` is provided.
    - Otherwise, fetch all books with pagination.
    """
    try:
        result = main_crud.get_book(db, book_id=book_id, skip=skip, limit=limit)
        if book_id is not None and result is None:
            return JSONResponse(status_code=404, content={"detail": "Book not found"})
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error: {e}"})

# Update a book
@router.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    try:
        db_book = main_crud.update_book(db, book_id=book_id, book=book)
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
        db_book = main_crud.delete_book(db, book_id=book_id)
        if db_book is None:
            return JSONResponse(status_code=404, content="Book not found")
        return db_book
    except Exception as E:
        return JSONResponse(status_code=500,content=f'error due to {E}')
    





@router2.get("/users/")
def read_users(
    user_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    - Fetch a single user if `user_id` is provided.
    - Otherwise, fetch all users with pagination.
    """
    try:
        result = main_crud.get_user(db, user_id=user_id, skip=skip, limit=limit)
        if user_id is not None and result is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error: {e}"})
    
@router2.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return main_crud.create_user(db=db, user=user)   

# soft delete a user
@router2.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = main_crud.delete_user(db, user_id=user_id)
        if db_user is None:
            return JSONResponse(status_code=404, content="User not found")
        return db_user
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
    




@router3.get("/loans/")
def read_loans_route(
    loan_id: int | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    - Fetch a single loan if `loan_id` is provided.
    - Otherwise, fetch all loans with pagination.
    """
    try:
        result = main_crud.get_loan(db, loan_id=loan_id, skip=skip, limit=limit)
        if loan_id is not None and result is None:
            return JSONResponse(status_code=404, content={"detail": "Loan not found"})
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Error: {e}"})  


# Create a new loan (borrow a book)
@router3.post("/loans/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    try:
        return main_crud.create_loan(db=db, loan=loan)
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
    

@router3.put('/loan/{id}')
def return_book(id,db:Session=Depends(get_db)):
    try:
        db_loan = main_crud.return_book(db, loan_id=id)
        if db_loan is None:
            return JSONResponse(status_code=404, content="Loan not found or already returned")
        return JSONResponse(status_code=200,content=f"return sucess for Lone_id:{db_loan.id},user_id:{db_loan.user_id} and book_id : {db_loan.book_id}")
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}') 



@router3.post("/loans/overdue-check/")
def check_overdue_loans(db: Session = Depends(get_db)):
    try:
        updated_loans = main_crud.check_and_update_overdue_loans(db)
        return {"message": f"Checked and updated {len(updated_loans)} overdue loans."}
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')

#soft delete a loan
@router3.delete("/loans/{loan_id}", response_model=schemas.Loan)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        db_loan = main_crud.delete_loan(db, loan_id=loan_id)
        if db_loan is None:
            return JSONResponse(status_code=404, content="Loan not found")
        return db_loan
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
    

#audit tables
@router4.get("/audit/")
def audit_record(db: Session = Depends(get_db)):
    try:
        return main_crud.audit_record(db=db)
    except Exception as e:
        return JSONResponse(status_code=500,content=f'error due to {e}')