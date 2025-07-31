from fastapi import APIRouter, Query, Depends, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas.community import *
from app.schemas.user import User
from app.core.dependencies import get_current_user, get_db
from app.crud import community as community_crud

router = APIRouter()


@router.get("/")
async def get_community(
    id: Optional[int] = Query(None, ge=0),
    owner_id: Optional[int] = Query(None, ge=0),
    community_name: Optional[str] = Query(None, max_length=50),
    db: Session = Depends(get_db)
) -> List[Community]:
    
    if id or owner_id or community_name:
        filters = CommunityFilter(
            id=id,
            owner_id=owner_id,
            community_name=community_name
        )
        return community_crud.get_communities_by_conditionals(db, filters)
    return community_crud.get_all_communities(db)


@router.post("/")
async def create_community(
    community: CommunityBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Community:
    
    new_community = CommunityCreate(
        community_name=community.community_name,
        description=community.description,
        photo_url=community.photo_url,
        owner_id=current_user.id #Get user id via jwt cookie
    )

    return community_crud.create_community(db, new_community)

@router.put("/{community_id}")
async def update_community(
    updates: CommunityUpdate,
    community_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Community:
    
    community = community_crud.get_communities_by_conditionals(db, CommunityFilter(id=community_id))
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    community = community[0]

    if community.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You have not permissions to edit other communities")
    
    return community_crud.update_community(db, community_id, updates)

@router.delete("/{community_id}")
async def delete_community(
    community_id: int = Path(..., ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    
    community = community_crud.get_communities_by_conditionals(db, CommunityFilter(id=community_id))
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    community = community[0]

    if community.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You have not permissions to edit other communities")
    
    return community_crud.delete_community(db, community_id)