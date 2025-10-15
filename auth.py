from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import model
from config import get_db

# -------------------- JWT CONFIG --------------------
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# -------------------- Password Context --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------- Hashing Password --------------------
def get_password_hash(password: str) -> str:
    """
    Hash the password using bcrypt safely.
    Truncate to 72 bytes to avoid bcrypt limit issues.
    """
    password_bytes = password.encode("utf-8")[:72]
    return pwd_context.hash(password_bytes)

# -------------------- Verifying Password --------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the provided plain password against the hashed password.
    """
    plain_bytes = plain_password.encode("utf-8")[:72]
    return pwd_context.verify(plain_bytes, hashed_password)

# -------------------- TOKEN CREATION --------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    if "sub" not in to_encode and "email" in to_encode:
        to_encode["sub"] = to_encode["email"]
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -------------------- OAUTH2 SCHEME --------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# -------------------- CURRENT USER --------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        role: str = payload.get("role", "USER")
        user_id: int = payload.get("id")
    except JWTError:
        raise credentials_exception

    user = db.query(model.User).filter(model.User.email == email, model.User.is_deleted == False).first()
    if user is None:
        raise credentials_exception
    return user

# -------------------- ROLE-BASED AUTH --------------------
def admin_required(current_user: model.User = Depends(get_current_user)):
    if current_user.role != model.Roles.ADMIN:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def user_or_admin(current_user: model.User = Depends(get_current_user)):
    return current_user

# -------------------- GENERIC ROLE CHECK --------------------
def role_required(required_role: model.Roles):
    def role_checker(current_user: model.User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail=f"{required_role.name} privileges required")
        return current_user
    return role_checker
