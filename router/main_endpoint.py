from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config import engine, get_db
import schemas, model, auth
from crud import main_crud
# Routers
router=APIRouter(tags=["LOGIN"])
router1 = APIRouter(tags=["Users"])
router2 = APIRouter(tags=["Books"])
router3 = APIRouter(tags=["Loans"])
router4 = APIRouter(tags=["Audit"])

# Create tables
model.Base.metadata.create_all(bind=engine)

# -------------------- LOGIN --------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.email == form_data.username, model.User.is_deleted == False).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    token_data = {"sub": user.email, "id": user.id, "role": user.role.value}
    access_token = auth.create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

# -------------------- BOOKS --------------------
@router2.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.create_book(db=db, book=book)

@router2.get("/books/")
def read_books_route(book_id: int | None = Query(None), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: model.User = Depends(auth.user_or_admin)):
    return main_crud.get_book(db, book_id=book_id, skip=skip, limit=limit)

@router2.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.update_book(db, book_id=book_id, book=book)

@router2.delete("/books/{book_id}", response_model=schemas.Book)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.delete_book(db, book_id=book_id)

# -------------------- USERS --------------------
@router1.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return main_crud.create_user(db=db, user=user)

@router1.get("/users/")
def read_users(user_id: int | None = Query(None), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.get_user(db, user_id=user_id, skip=skip, limit=limit)

@router1.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.delete_user(db, user_id=user_id)

# -------------------- LOANS --------------------
@router3.post("/loans/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db), current_user: model.User = Depends(auth.user_or_admin)):
    if current_user.role != model.Roles.ADMIN and current_user.id != loan.user_id:
        raise HTTPException(status_code=403, detail="Cannot borrow for another user")
    return main_crud.create_loan(db=db, loan=loan)

@router3.get("/loans/")
def read_loans_route(loan_id: int | None = Query(None), skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: model.User = Depends(auth.user_or_admin)):
    return main_crud.get_loan(db, loan_id=loan_id, skip=skip, limit=limit)

@router3.put('/loan/{id}')
def return_book(id: int, db: Session = Depends(get_db), current_user: model.User = Depends(auth.user_or_admin)):
    return main_crud.return_book(db, loan_id=id)

@router3.post("/loans/overdue-check/")
def check_overdue_loans(db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.check_and_update_overdue_loans(db)

@router3.delete("/loans/{loan_id}", response_model=schemas.Loan)
def delete_loan(loan_id: int, db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.delete_loan(db, loan_id=loan_id)

# -------------------- AUDIT --------------------
@router4.get("/audit/")
def audit_record(db: Session = Depends(get_db), current_user: model.User = Depends(auth.admin_required)):
    return main_crud.audit_record(db=db)
