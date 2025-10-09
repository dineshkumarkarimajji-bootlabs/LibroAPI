from sqlalchemy.orm import Session
from fastapi import HTTPException
import model, schemas
from datetime import datetime,timezone


#get Loan by id
def get_loan(db: Session, loan_id: int):
    return db.query(model.Loan).filter(model.Loan.id == loan_id, model.Loan.Softdelete == 0).first()    

# get all loans
def get_loans(db: Session, skip: int = 0, limit: int = 10):
    return db.query(model.Loan).filter(model.Loan.Softdelete == 0).offset(skip).limit(limit).all()  
# Create a new loan (borrow a book)
def create_loan(db: Session, loan: schemas.LoanCreate):
    try:
        with db.begin():
            db_book = db.query(model.Book).filter(model.Book.id == loan.book_id, model.Book.BookAvl == 0).first()
            db_user = db.query(model.User).filter(model.User.id == loan.user_id, model.User.Membership == 0).first()

            if db_book is None:
                raise HTTPException(status_code=404, detail="Book not found or unavailable")
            if db_user is None:
                raise HTTPException(status_code=404, detail="User not found or inactive")
            if db_book.available_copies < 1:
                raise HTTPException(status_code=400, detail="No available copies to borrow")

            db_loan = model.Loan(
                book_id=loan.book_id,
                user_id=loan.user_id
            )
            db_book.available_copies -= 1  # Decrease available copies
            db.add(db_loan)
        return db_loan
    except:
        raise HTTPException(status_code=500,detail="bad request")


# Return a book
def return_book(db: Session, loan_id: int): 
    try:
        with db.begin():
            db_loan = get_loan(db, loan_id)
            if db_loan is None:
                raise HTTPException(status_code=404, detail="Loan not found")
            if db_loan.status == model.LoanStatus.returned:
                raise HTTPException(status_code=400, detail="Book already returned")

            db_book = db.query(model.Book).filter(model.Book.id == db_loan.book_id, model.Book.BookAvl == 0).first()
            if db_book is None:
                raise HTTPException(status_code=404, detail="Book not found")

            db_loan.return_date = datetime.now(timezone.utc)
            db_loan.status = model.LoanStatus.returned
            db_book.available_copies += 1  # Increase available copies
            
        return db_loan
    except:
        return("it is return book not working")

#get all overdue loans
def get_overdue_loans(db: Session):
    now = datetime.datetime.utcnow()
    return db.query(model.Loan).filter(model.Loan.due_date < now, model.Loan.status == model.LoanStatus.borrowed, model.Loan.Softdelete == 0).all() 

# soft delete a loan
def delete_loan(db: Session, loan_id: int):
    db_loan = get_loan(db, loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    db_loan.Softdelete = 1  # Mark as deleted
    db.commit()
    return db_loan

# Check and update overdue loans
def check_and_update_overdue_loans(db: Session):
    now = datetime.now(timezone.utc)
    overdue_loans = db.query(model.Loan).filter(
        model.Loan.due_date < now,
        model.Loan.status == model.LoanStatus.borrowed,
        model.Loan.Softdelete == 0
    ).all()
    for loan in overdue_loans:
        loan.status = model.LoanStatus.overdue
    db.commit()
    return overdue_loans