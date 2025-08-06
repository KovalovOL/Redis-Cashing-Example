from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.models import Post as PostDB
from app.schemas.post import *


def get_all_posts(
    db: Session, 
    limit: int,
    offset: int
) -> List[PostDB]:
    return db.query(PostDB).offset(offset).limit(limit).all()


def get_posts_by_conditions(
    db: Session, 
    limit: int,
    offset: int,
    owner_id: Optional[int],
    community_id: Optional[int]
) -> List[PostDB]:
    conditions = []

    if owner_id is not None:
        conditions.append(PostDB.owner_id == owner_id)

    if community_id is not None:
        conditions.append(PostDB.community_id == community_id)

    return (
        db.query(PostDB)
        .filter(*conditions)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_post_by_id(
    db: Session,
    post_id: int
) -> PostDB:
    return db.query(PostDB).filter(PostDB.id == post_id).first()


def create_post(
    db: Session,
    post: PostCreate
) -> PostDB:
    new_post = PostDB(
        title=post.title,
        text=post.text,
        owner_id=post.owner_id,
        community_id=post.community_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


def update_post(
    db: Session,
    post: PostDB
) -> PostDB:
    db.commit()
    db.refresh(post)

    return post 


def delete_post(
    db: Session,
    post: PostDB
) -> PostDB:
    db.delete(post)
    db.commit()

    return post