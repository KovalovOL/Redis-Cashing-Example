from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.models import Community as CommunityDB
from app.schemas.community import *



def get_all_communities(db: Session) -> List[Community]:
    communities = db.query(CommunityDB).all()
    return [Community.from_orm(com) for com in communities]


def get_communities_by_conditionals(db: Session, filter: CommunityFilter) -> List[Community]:
    conditions = []

    if filter.id is not None:
        conditions.append(CommunityDB.id == filter.id)
    if filter.community_name is not None:
        conditions.append(CommunityDB.community_name == filter.community_name)
    if filter.owner_id is not None:
        conditions.append(CommunityDB.owner_id == filter.owner_id)

    communities = db.query(CommunityDB).filter(*conditions).all()
    return [Community.from_orm(com) for com in communities]


def create_community(db: Session, community: CommunityCreate) -> Community:
    new_community = CommunityDB(
        community_name = community.community_name,
        description = community.description,
        photo_url = community.photo_url,
        owner_id = community.owner_id
    )

    db.add(new_community)
    db.commit()
    db.refresh(new_community)

    return Community.from_orm(new_community)


def update_community(db: Session, community_id: int, updates: CommunityUpdate) -> Community:
    community = db.query(CommunityDB).filter(CommunityDB.id == community_id).first()

    if not community:
        raise HTTPException(status_code=404, detail=f"Community with id {community_id} not found")
    
    if updates.community_name is not None:
        community.community_name = updates.community_name
    if updates.description is not None:
        community.description = updates.description
    if updates.photo_url is not None:
        community.photo_url = updates.photo_url

    db.commit()
    db.refresh(community)

    return Community.from_orm(community)


def delete_community(db: Session, community_id: int) -> dict:
    community = db.query(CommunityDB).filter(CommunityDB.id == community_id).first()

    if not community:
        raise HTTPException(status_code=404, detail=f"Community with id {community_id} not found")

    db.delete(community)
    db.commit()

    return {"message": f"Community {community.community_name} has been deleted"}