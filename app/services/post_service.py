from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.schemas.post import *
from app.schemas.user import User
from app.crud import post as post_crud
from app.cache.utils import *
from app.cache.keys import post_cache_key
from app.core.logging_config import logger
from app.core.log_context import set_user_context



def get_all_post(
    db: Session,
    limit: int,
    offset: int,
    owner_id: int,
    community_id: int,
) -> List[Post]:
    posts = post_crud.get_posts_by_conditions(db, limit, offset, owner_id, community_id)
    logger.info("posts_fetched_from_db", total_count=len(posts))

    return [Post.from_orm(p) for p in posts]


def get_post_by_id(
    db: Session,
    post_id: int      
) -> Post:
    post_key = post_cache_key(post_id)
    post = deserialize_post(get_cache(post_key))
    if post:
        logger.info("post_fetched_from_cache", post_id=post_id)
        return post

    post = post_crud.get_post_by_id(db, post_id)
    if not post:
        logger.warning(
            "post_fetch_failed",
            post_id=post_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    set_cache(post_key, serialize_post(post), ttl=120)
    logger.debug("post_cached", post_id=post_id)

    logger.info("post_fetched_from_db", post_id=post_id)
    return Post.from_orm(post)



def create_post(
    db: Session,
    post: PostCreateInput,
    current_user: User
) -> Post:
    set_user_context(current_user)

    new_post = PostCreate(
        title=post.title,
        text=post.text,
        community_id=post.community_id,
        owner_id=current_user.id
    )

    post_data = post_crud.create_post(db, new_post)
    logger.info("post_created", post_id=post_data.id)

    set_cache(post_cache_key(post_data.id), serialize_post(post_data), ttl=120)
    logger.debug("post_cached", post_id=post_data.id)

    return Post.from_orm(post_data)


def update_post(
    db: Session,
    post_id: int,
    updates: PostUpdate,
    current_user: User
) -> Post:
    set_user_context(current_user)

    post = post_crud.get_post_by_id(db, post_id)
    if not post:
        logger.info(
            "post_update_failed",
            post_id=post_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404, 
            detail="Post not found"
        )

    if current_user.id != post.owner_id and current_user.role != "admin":
        logger.warning(
            "post_update_failed",
            post_id=post_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to edit other posts"
        )
    
    if updates.title is not None:
        post.title = updates.title
        post.is_edited=True
        post.time_edited=datetime.utcnow()

    if updates.text is not None:
        post.text = updates.text
        post.is_edited=True
        post.time_edited=datetime.utcnow()

    updated_post = post_crud.update_post(db, post)
    logger.info("post_updated", post_id=post_id)

    set_cache(post_cache_key(post_id), serialize_post(updated_post), ttl=120)
    logger.info("post_cached", post_id=post_id)

    return Post.from_orm(updated_post)


def delete_post(
    db: Session,
    post_id: int,
    current_user: User
) -> dict:
    set_user_context(current_user)

    post = post_crud.get_post_by_id(db, post_id)
    if not post:
        logger.info(
            "post_delete_failed",
            post_id=post_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404, 
            detail="Post not found"
        )

    if current_user.id != post.owner_id and current_user.role != "admin":
        logger.warning(
            "post_delete_failed",
            post_id=post_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete other posts"
        )

    post_crud.delete_post(db, post)
    logger.info("post_deleted", post_id=post_id)

    delete_cache(post_cache_key(post_id))
    logger.info("post_cache_deleted", post_id=post_id)

    return {"message": f"Post with id {post_id} has been deleted"}

    
