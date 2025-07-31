from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.core.dependencies import get_db, get_current_user
from app.crud.user import create_user, get_users_by_conditions
from app.db.models import User as UserDB
from app.schemas.user import UserCreate, UserFilter, UserLogin, User


router = APIRouter()


@router.post("/register")
async def register_user(
    new_user: UserLogin, db: Session = Depends(get_db)
):
    
    user = create_user(
        db,
        UserCreate(
            username=new_user.username,
            password=new_user.password,
            role="user"
        )
    )
    return {"message": f"User {user.username} has been created"}


@router.post("/login")
async def login_user(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail=f"User {data.username} not found")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="User or password incorrect")
    
    token = create_access_token({"sub": user.username, "role": user.role})
    response.set_cookie(key="access_token", value=token, httponly=True)
    return {
        "message": f"User {user.username} has been logged in",
        "token": token    
    }


@router.get("/me")
async def get_user_by_jwt(current_user: User = Depends(get_current_user)) -> User:
    return current_user





    