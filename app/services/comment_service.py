from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import comment as comment_crud
from app.crud.post import get_post_by_id
from app.schemas.user import User
from app.schemas.comment import CommentCreate, CommentCreateInput, Comment, CommentUpdate
from app.core.log_context import set_user_context
from app.core.logging_config import logger


def get_comments_by_post(
    db: Session,
    post_id: int,
    limit: int,
    offset: int,
) -> List[Comment]:
    
    if not get_post_by_id(db, post_id):
        logger.warning(
            "comments_fetch_failed",
            post_id=post_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    comments = comment_crud.get_all_comments_by_post(db, post_id, limit, offset)
    logger.info("comments_fetched_from_db", post_id=post_id, total_count=len(comments))

    return [Comment.from_orm(c) for c in comments]


def create_comment(
    db: Session,
    comment: CommentCreateInput,
    current_user: User
) -> Comment:
    set_user_context(current_user)

    if not get_post_by_id(db, comment.post_id):
        logger.warning(
            "comments_fetch_failed",
            post_id=comment.post_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    new_comment = CommentCreate(
        text=comment.text,
        post_id=comment.post_id,
        owner_id=current_user.id
    )

    comment_data = comment_crud.create_comment(db, new_comment)
    logger.info("comment_created", comment_id=comment_data.id)

    return Comment.from_orm(comment_data)


def update_comment(
    db: Session,
    comment_id: int,
    updates: CommentUpdate,
    current_user: User
) -> Comment:
    set_user_context(current_user)

    comment = comment_crud.get_comment_by_id(db, comment_id)
    if not comment:
        logger.warning(
            "comment_updatefailed",
            comment_id=comment_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    
    if comment.owner_id != current_user.id and current_user.role != "admin":
        logger.warning(
            "comment_update_failed",
            comment_id=comment_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )
    
    if updates.text is not None:
        comment.text = updates.text
        comment.is_edited = True
        comment.time_edited = datetime.utcnow()

    comment_crud.update_comment(db, comment)
    logger.info("comment_updated", comment_id=comment_id)

    return Comment.from_orm(comment)
    


def delete_comment(
    db: Session,
    comment_id: int,
    current_user: User
) -> dict:
    set_user_context(current_user)

    comment = comment_crud.get_comment_by_id(db, comment_id)
    if not comment:
        logger.warning(
            "comment_delete_failed",
            comment_id=comment_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )
    
    if comment.owner_id != current_user.id and current_user.role != "admin":
        logger.warning(
            "comment_delete_failed",
            comment_id=comment_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )
    

    comment_crud.delete_comment(db, comment)
    logger.info("comment_deleted", comment_id=comment_id)

    return {"message": f"Comment {comment_id} has been deleted"}