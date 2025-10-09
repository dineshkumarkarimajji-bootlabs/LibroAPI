from sqlalchemy.orm import Session
from fastapi import HTTPException
import model, schemas




# create new user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = model.User(
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# get user by id
def get_user(db: Session, user_id: int):
    return db.query(model.User).filter(model.User.id == user_id, model.User.Membership == 0).first()    

# get all users
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(model.User).filter(model.User.Membership == 0).offset(skip).limit(limit).all()

# Soft delete a user
def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.Membership = 1  # Mark as deleted
    db.commit()
    return db_user