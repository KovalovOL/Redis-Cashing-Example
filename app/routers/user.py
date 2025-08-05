from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from typing import List

from app.services import user_service
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import *
from app.schemas.community import Community


router = APIRouter()


@router.get("/", response_model=List[User])
async def get_all_users_handler(
    db: Session = Depends(get_db)
) -> List[User]:
    return user_service.get_all_users(db)


@router.get("/me", response_model=User)
async def get_logged_in_user_handler(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user


@router.get("/{username}", response_model=User)
async def get_user_by_username_handler(
    username: str = Path(..., max_length=50),
    db: Session = Depends(get_db)
) -> User:
    return user_service.get_user_by_username(db, username)


@router.get("/me/subscribes", response_model=List[Community])
async def get_current_user_subscribes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Community]:
    return user_service.get_current_user_subscribes(db, current_user)

@router.get("/{user_id}/subscribes", response_model=List[Community])
async def get_user_subscribes(
    user_id: int = Path(..., ge=0),
    db: Session = Depends(get_db)
) -> List[Community]:
    return user_service.get_user_subscribes(db, user_id)


@router.post("/", response_model=User)
async def create_user_handler(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    return user_service.create_user(db, user, current_user)


@router.put("/{user_id}", response_model=User)
async def update_user_handler(
    updates: UserUpdate,
    user_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    return user_service.update_user(db, user_id, updates, current_user)


@router.delete("/{user_id}", response_model=dict)
async def delete_user_handler(
    user_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    return user_service.delete_user(db, user_id, current_user)
