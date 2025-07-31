from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session

from jose import jwt, JWTError

from app.db.database import Sessionmaker
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.jwt_token import Token
from app.schemas.user import UserFilter, User
from app.crud.user import get_users_by_conditions


def get_db():
    db = Sessionmaker()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Access token not found")
    
    try:
        paylaod = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token = Token(**paylaod)
    except(JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid tokne")
    
    user = get_users_by_conditions(db, UserFilter(username=token.sub))
    if not user:
        raise HTTPException(status_code=401, detail=f"User {token.sub} not found")
    user = user[0]

    return user
