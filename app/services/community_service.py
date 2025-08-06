from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import community as community_crud
from app.crud import user as user_crud
from app.db.models import Community as CommunityDB
from app.schemas.community import *
from app.schemas.user import User
from app.schemas.post import Post
from app.cache.utils import *
from app.cache.keys import community_cache_key
from app.core.logging_config import logger
from app.core.log_context import set_user_context



def get_all_communities(
        db: Session,
        limit: int,
        offset: int
) -> List[Community]:
    communities = community_crud.get_all_communities(db, limit, offset)
    logger.info(
        "communities_fetched_from_db",
        total_count=len(communities)
    )
    return [Community.from_orm(community) for community in communities]


def get_community_by_id(
    db: Session,
    community_id: int
) -> Community:
    cache_key = community_cache_key(community_id)
    cached_community = get_cache(cache_key)
    if cached_community:
        logger.info("fetched_community_from_cache", community_id=community_id)
        return deserialize_community(cached_community)

    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        logger.warning(
            "community_fetch_failed",
            community_id=community_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    logger.info("community_fetched_from_db", community_id=community_id)

    set_cache(cache_key, serialize_community(community), ttl=120)
    logger.debug("community_cached", community_id=community_id)

    return Community.from_orm(community)


def create_community(
    db: Session,
    community: CommunityCreateInput,
    current_user: User
) -> Community:
    set_user_context(current_user)

    if community_crud.is_community_exist_by_name(db, community.community_name):
        logger.warning(
            "community_create_failed",
            community_name=community.community_name,
            reason="already_exist"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Community {community.community_name} has already existed"
        )
    
    new_community = CommunityDB(
        community_name=community.community_name,
        description=community.description,
        photo_url=community.photo_url,
        owner_id=current_user.id
    )

    community_crud.create_community(db, new_community)
    logger.info("community_created", community_id=new_community.id)

    set_cache(community_cache_key(new_community.id), serialize_community(new_community), ttl=120)
    logger.debug("community_cached", community_id=new_community.id)

    return Community.from_orm(new_community)


def update_community(
    db: Session,
    community_id: int,
    updates: CommunityUpdate,
    current_user: User
) -> Community:
    set_user_context(current_user)

    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        logger.warning(
            "community_update_failed",
            community_id=community_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    

    if community.owner_id != current_user.id and current_user.role != "admin":
        logger.warning(
            "community_update_failed",
            community_id=community_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to edit other communities"
        )

    if not updates.model_dump(exclude_unset=True):
        logger.warning(
            "community_update_failed",
            community_id=community_id,
            reason="data_missed"
        )
        raise HTTPException(
            status_code=400,
            detail="No update fields provided"
        )

    if updates.community_name is not None:
        if community_crud.is_community_exist_by_name(db, updates.community_name):
            logger.warning(
                "community_update_failed",
                community_name=updates.community_name,
                reason="already_exists"
            )
            raise HTTPException(
                status_code=409, detail=f"Community {updates.community_name} has already existed"
            )
        community.community_name = updates.community_name
    
    if updates.description is not None:
        community.description = updates.description
    
    if updates.photo_url is not None:
        community.photo_url = updates.photo_url

    community_crud.update_community(db, community)
    logger.info("community_updated", community_id=community_id)

    set_cache(community_cache_key(community_id), serialize_community(community), ttl=120)
    logger.debug("community_cached", community_id=community_id)

    return Community.from_orm(community)


def delete_community(
    db: Session,
    community_id: int,
    current_user: User
) -> dict:
    set_user_context(current_user)

    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        logger.warning(
            "community_delete_failed",
            community_id=community_id,
            reason="not_foundt"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    
    if community.owner_id != current_user.id and current_user.role != "admin":
        logger.warning(
            "community_delete_failed",
            community_id=community_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete other communities"
        )
    
    community_crud.delete_community(db, community)
    logger.info("community_deleted", community_id=community_id)

    delete_cache(community_cache_key(community_id))
    logger.debug("community_cache_deleted", community_id=community_id)

    return {"message": f"Community {community.community_name} has been deleted"} 


def get_followers(
    db: Session,
    limit: int,
    offset: int,
    community_id: int
) -> List[User]:
    if not community_crud.get_community_by_id(db, community_id):
        logger.warning(
            "community_fetch_followers_failed",
            community_id=community_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )

    logger.info("community_followerd_fetched_from_db", community_id=community_id)
    return [User.from_orm(user) for user in community_crud.get_all_followers(db, limit, offset, community_id)]


def add_follower(
    db: Session,
    community_id: int,
    current_user: User
) -> List[User]:
    set_user_context(current_user)

    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        logger.warning(
            "community_add_follower_failed",
            community_id=community_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    
    
    follower=user_crud.get_user_by_id(db, current_user.id)
    if follower in community.followers:
        logger.warning(
            "community_add_follower_failed",
            community_id=community_id,
            follower_id=current_user.id,
            reason="follower_is_exist"
        )
        raise HTTPException(
            status_code=409,
            detail="Follower already exist"
        )

    updated_community = community_crud.add_follower(db, follower, community)

    logger.info("community_added_follower", community_id=community_id)
    return [User.from_orm(user) for user in updated_community.followers]


def delete_follower(
    db: Session,
    community_id: int,
    current_user: User
) -> dict:
    set_user_context(current_user)

    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        logger.warning(
            "community_add_follower_failed",
            community_id=community_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )

    follower = user_crud.get_user_by_id(db, current_user.id)
    if not follower in community.followers:
        logger.warning(
            "community_follower_delete_failed",
            community_id=community_id,
            follower_id=current_user.id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="User does not sunscribed"
        )
    
    updated_community = community_crud.delete_follower(db, follower, community)
    logger.info("community_follower_deleted", community_id=community_id)

    return {"message": f"follower {follower.username} has been deleted"}


def get_posts(
    db: Session,
    community_id: int,
    limit: int,
    offset: int
) -> List[Post]:
    
    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        logger.warning(
            "community_add_follower_failed",
            community_id=community_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    
    posts = community_crud.get_community_posts(db, community_id, limit, offset)
    logger.info("community_posts_fetched_from_db", community_id=community_id, total_count=len(posts))

    return [Post.from_orm(p) for p in posts]