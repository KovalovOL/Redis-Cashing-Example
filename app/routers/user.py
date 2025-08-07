from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import List

from app.services import user_service
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import *
from app.schemas.community import Community
from app.schemas.post import Post


router = APIRouter()


@router.get("/", response_model=List[User])
async def get_all_users_handler(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[User]:
    return user_service.get_all_users(db, limit, offset)





@router.get("/{user_id}", response_model=User)
async def get_user_by_id_handler(
    user_id: str = Path(..., max_length=50),
    db: Session = Depends(get_db)
) -> User:
    return user_service.get_user_by_id(db, user_id)





@router.get("/{user_id}/subscribes", response_model=List[Community])
async def get_user_subscribes(
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: int = Path(..., ge=0),
    db: Session = Depends(get_db)
) -> List[Community]:
    return user_service.get_user_subscribes(db, user_id, limit, offset)


@router.get("/{user_id}/posts")
async def get_user_posts(
    user_id: int = Path(..., gt=0),
    limit: int = Query(5, gt=0, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[Post]:
    return user_service.get_user_pots(db, user_id, limit, offset)



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
