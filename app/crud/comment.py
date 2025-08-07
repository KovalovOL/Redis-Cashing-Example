from typing import List
from sqlalchemy.orm import Session

from app.db.models import Comment as CommentDB
from app.schemas.comment import CommentCreate



def get_all_comments_by_post(
    db: Session,
    post_id: int,
    limit: int,
    offset: int
) -> List[CommentDB]:
    return (
        db.query(CommentDB)
        .filter(CommentDB.post_id == post_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_comment_by_id(
    db: Session,
    comment_id: int
) -> CommentDB:
    return db.query(CommentDB).filter(CommentDB.id == comment_id).first()


def create_comment(
    db: Session,
    comment: CommentCreate
) -> CommentDB:
    new_comment = CommentDB(
        text=comment.text,
        owner_id=comment.owner_id,
        post_id=comment.post_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


def update_comment(
    db: Session,
    comment: CommentDB
) -> CommentDB:
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(
    db: Session,
    comment: CommentDB
) -> CommentDB:
    db.delete(comment)
    db.commit()
    return comment