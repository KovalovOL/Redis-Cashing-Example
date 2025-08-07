from typing import List
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.services import comment_service
from app.core.dependencies import get_db, get_current_user
from app.schemas.comment import Comment, CommentCreateInput, CommentUpdate
from app.schemas.user import User


router = APIRouter()



@router.get("/{post_id}" ,response_model=List[Comment])
async def get_all_comments_by_post(
    post_id: int = Path(..., gt=0),
    limit: int = Query(5, gt=0, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[Comment]:
    return comment_service.get_comment_by_post(db, post_id, limit, offset)


@router.post("/{post_id}", response_model=Comment)
async def create_comment(
    comment: CommentCreateInput,
    post_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Comment:
    return comment_service.create_comment(db, comment, post_id, current_user)


@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    updates: CommentUpdate,
    comment_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Comment:
    return comment_service.update_comment(db, comment_id, updates, current_user)



@router.delete("/{comment_id}", response_model=dict)
async def delele_comment(
    comment_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    return comment_service.delete_comment(db, comment_id, current_user)