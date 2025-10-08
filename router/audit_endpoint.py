from fastapi import FastAPI, Depends,HTTPException,APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from config import engine, sessionLocal
from model import Base
import crud, schemas
from router.book_endpoint import get_db


router4=APIRouter(tags=["Audit"])
#audit tables
@router4.get("/audit/")
def audit_record(db: Session = Depends(get_db)):
    try:
        return crud.audit_record(db=db)
    except Exception as e:
        return JSONResponse(status_code=500,content=f'error due to {e}')