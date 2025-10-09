from fastapi import FastAPI, Depends,APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from crud import users_crud
import schemas
from router.book_endpoint import get_db

router2 = APIRouter(tags=['users'])



@router2.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = users_crud.get_user(db, user_id=user_id)
        if db_user is None:
            return JSONResponse(status_code=404, content="User not found")
        return db_user
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
# Get all users
@router2.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = users_crud.get_users(db, skip=skip, limit=limit)
        return users
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
    
@router2.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return users_crud.create_user(db=db, user=user)   

# soft delete a user
@router2.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = users_crud.delete_user(db, user_id=user_id)
        if db_user is None:
            return JSONResponse(status_code=404, content="User not found")
        return db_user
    except Exception as e:
        return JSONResponse(status_code=500,content=f'erroe due to {e}')
    

    