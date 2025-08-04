from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import Session

from jose import jwt

from app.db.database import Sessionmaker
from app.core.security import SECRET_KEY, ALGORITHM
from app.core.log_context import user_id_ctx, user_role_ctx
from app.schemas.jwt_token import Token
from app.schemas.user import User
from app.crud.user import get_user_by_username



def get_db():
    db = Sessionmaker()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token not found"
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token = Token(**payload)
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )
    
    user = get_user_by_username(db, token.sub)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User f{token.sub} not found"
        )

    return User.from_orm(user)