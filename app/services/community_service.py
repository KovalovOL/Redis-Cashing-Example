from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import community as community_crud
from app.db.models import Community as CommunityDB
from app.schemas.community import *
from app.schemas.user import User
from app.cache.utils import *
from app.cache.keys import *


def get_all_communities(db: Session) -> List[Community]:
    communities = community_crud.get_all_communities(db)
    return [Community.from_orm(community) for community in communities]


def get_community_by_id(
    db: Session,
    community_id: int
) -> Community:
    cache_key = community_cache_key(community_id)
    cached_community = get_cache(cache_key)
    if cached_community:
        print("Data from cache")
        return deserialize_community(cached_community)

    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    set_cache(cache_key, serialize_community(community), ttl=120)
    return Community.from_orm(community)


def create_community(
    db: Session,
    community: CommunityCreateInput,
    current_user: User
) -> Community:
    
    if community_crud.is_community_exist_by_name(db, community.community_name):
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
    return Community.from_orm(new_community)


def update_community(
    db: Session,
    community_id: int,
    updates: CommunityUpdate,
    current_user: User
) -> Community:
    
    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    

    if community.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to edit other communities"
        )

    if not updates.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=400,
            detail="No update fields provided"
        )

    if updates.community_name is not None:
        if community_crud.is_community_exist_by_name(db, updates.community_name):
            raise HTTPException(
                status_code=409, detail=f"Community {updates.community_name} has already existed"
            )
        community.community_name = updates.community_name
    
    if updates.description is not None:
        community.description = updates.description
    
    if updates.photo_url is not None:
        community.photo_url = updates.photo_url

    community_crud.update_community(db, community)
    set_cache(community_cache_key(community_id), serialize_community(community), ttl=120)
    return Community.from_orm(community)


def delete_community(
    db: Session,
    community_id: int,
    current_user: User
) -> dict:
    community = community_crud.get_community_by_id(db, community_id)
    if not community:
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )
    
    if community.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete other communities"
        )
    
    community_crud.delete_community(db, community)
    delete_cache(community_cache_key(community_id))
    return {"message": f"Community {community.community_name} has been deleted"} 