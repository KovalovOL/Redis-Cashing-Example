from fastapi import APIRouter, Response
from sqlalchemy.orm import Session

from app.services import auth_service
from app.core.dependencies import *
from app.schemas.user import UserCreate, UserLogin


router = APIRouter()


@router.post("/register", response_model=User)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    return auth_service.register_user(user, db)

@router.post("/login", response_model=dict)
async def login_user(
    user: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
) -> dict:
    return auth_service.login_user(user, response, db)


@router.get("/me", response_model=User)
async def get_user_by_jwt(current_user: User = Depends(get_current_user)):
    return current_user
    




    