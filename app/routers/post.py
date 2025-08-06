from fastapi import APIRouter, Path, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services import post_service
from app.core.dependencies import get_db, get_current_user
from app.schemas.user import User
from app.schemas.post import *



router = APIRouter()


@router.get("/")
async def get_all_posts(
    community_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(5, gt=0, le=100),
    offset: int = Query(0, ge=0),
    owner_id: Optional[int] = Query(None, gt=0),
    db: Session = Depends(get_db)
) -> List[Post]:
    return post_service.get_all_post(db, limit, offset, owner_id, community_id)


@router.get("/{post_id}")
async def get_post_by_id(
    post_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
) -> Post:
    return post_service.get_post_by_id(db, post_id)


@router.post("/")
async def create_post(
    post: PostCreateInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Post:
    return post_service.create_post(db, post, current_user)


@router.put("/{post_id}")
async def update_post(
    updates: PostUpdate,
    post_id: int = Path(..., gl=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Post:
    return post_service.update_post(db, post_id, updates, current_user)


@router.delete("/{post_id}")
async def delete_post(
    post_id: int = Path(..., gl=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    return post_service.delete_post(db, post_id, current_user)
