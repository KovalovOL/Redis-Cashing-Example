from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, get_current_user
from app.schemas.community import *
from app.schemas.user import User
from app.schemas.post import Post
from app.services import community_service


router = APIRouter()


@router.get("/", response_model=List[Community])
async def get_all_communities_handler(
    db: Session = Depends(get_db),
    limit: int = Query(5, ge=0, le=100),
    offset: int = Query(0, ge=0)
) -> List[Community]:
    return community_service.get_all_communities(db, limit, offset)


@router.get("/{community_id}", response_model=Community)
async def get_community_by_name_handler(
    community_id: int = Path(..., ge=0),
    db: Session = Depends(get_db)
) -> Community:
    return community_service.get_community_by_id(db, community_id)




@router.get("/{community_id}/followers", response_model=List[User])
async def get_community_followers(
    community_id: int = Path(..., ge=0),
    limit: int = Query(5, ge=0, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[User]:
    return community_service.get_followers(db, limit, offset, community_id)


@router.post("/{community_id}/followers", response_model=List[User])
async def add_community_follower(
    community_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[User]:
    return community_service.add_follower(db, community_id, current_user)


@router.delete("/{community_id}/followers", response_model=dict)
async def delete_community_follower(
    community_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)   
) -> dict:
    return community_service.delete_follower(db, community_id, current_user)



@router.get("/{community_id}/posts")
def get_community_posts(
    community_id: int = Path(..., gl=0),
    limit: int = Query(5, gl=0, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> List[Post]:
    return community_service.get_posts(db, community_id, limit, offset)



@router.post("/", response_model=Community)
async def create_community(
    community: CommunityCreateInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Community:
    
    return community_service.create_community(db, community, current_user)


@router.put("/{community_id}", response_model=Community)
async def update_community(
    updates: CommunityUpdate,
    community_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Community:
    return community_service.update_community(db, community_id, updates, current_user)


@router.delete("/{community_id}", response_model=dict)
async def delete_community(
    community_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    return community_service.delete_community(db, community_id, current_user)