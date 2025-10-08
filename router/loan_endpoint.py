from fastapi import FastAPI, Depends,HTTPException,APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config import engine, sessionLocal
from model import Base
import crud, schemas
from router.book_endpoint import get_db
from model import Loan,Book,LoanStatus

router3 = APIRouter(tags=["Loans"])


# get all loans
@router3.get("/loans/", response_model=list[schemas.Loan])
def read_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        loans = crud.get_loans(db, skip=skip, limit=limit)
        return loans
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')

# get loan by id
@router3.get("/loans/{loan_id}")
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        data=db.query(Loan).filter(Loan.id==loan_id).first()
        if not  data:
            return JSONResponse(status_code=400,content="data is not generated")
        return data
    except Exception as error:
        return JSONResponse(status_code=404,content=f'error due to {error}')    


# Create a new loan (borrow a book)
@router3.post("/loans/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_loan(db=db, loan=loan)
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
    

@router3.put('/loan/{id}')
def return_book(id,db:Session=Depends(get_db)):
    try:
        db_loan = crud.return_book(db, loan_id=id)
        if db_loan is None:
            return JSONResponse(status_code=404, content="Loan not found or already returned")
        return JSONResponse(status_code=200,content=f"return sucess for Lone_id:{db_loan.id},user_id:{db_loan.user_id} and book_id : {db_loan.book_id}")
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}') 



@router3.post("/loans/overdue-check/")
def check_overdue_loans(db: Session = Depends(get_db)):
    try:
        updated_loans = crud.check_and_update_overdue_loans(db)
        return {"message": f"Checked and updated {len(updated_loans)} overdue loans."}
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')

#soft delete a loan
@router3.delete("/loans/{loan_id}", response_model=schemas.Loan)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    try:
        db_loan = crud.delete_loan(db, loan_id=loan_id)
        if db_loan is None:
            raise HTTPException(status_code=404, detail="Loan not found")
        return db_loan
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')