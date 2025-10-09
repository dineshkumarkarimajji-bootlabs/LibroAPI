from fastapi import  Depends,APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from crud import audit_crud
from router.book_endpoint import get_db


router4=APIRouter(tags=["Audit"])
#audit tables
@router4.get("/audit/")
def audit_record(db: Session = Depends(get_db)):
    try:
        return audit_crud.audit_record(db=db)
    except Exception as e:
        return JSONResponse(status_code=500,content=f'error due to {e}')