from sqlalchemy.orm import Session
from typing import List

from app.db.models import (
    Community as CommunityDB,
    User as UserDB,
    Post as PostDB
)
from app.schemas.community import CommunityCreate, CommunityFilter, CommunityUpdate



def get_all_communities(
        db: Session,
        limit: int,
        offset: int
) -> List[CommunityDB]:
    return db.query(CommunityDB).offset(offset).limit(limit).all()


def get_community_by_id(db: Session, community_id: int) -> CommunityDB:
    return db.query(CommunityDB).filter(CommunityDB.id == community_id).first()

def get_community_by_name(db: Session, name: str) -> CommunityDB:
    return db.query(CommunityDB).filter(CommunityDB.community_name == name).first()


def get_community_by_conditions(db: Session, filters: CommunityFilter) -> List[CommunityDB]:
    conditions = []

    if filters.id is not None:
        conditions.append(CommunityDB.id == filters.id)

    if filters.community_name is not None:
        conditions.append(CommunityDB.community_name == filters.community_name)

    if filters.owner_id is not None:
        conditions.append(CommunityDB.owner_id == filters.owner_id)

    return db.query(CommunityDB).filter(*conditions).all()


def create_community(db: Session, community: CommunityCreate) -> CommunityDB:
    new_community = CommunityDB(
        community_name=community.community_name,
        description=community.description,
        photo_url=community.photo_url,
        owner_id=community.owner_id
    )

    db.add(new_community)
    db.commit()
    db.refresh(new_community)
    return new_community


def update_community(db: Session, community: CommunityDB) -> CommunityDB:
    db.commit()
    db.refresh(community)
    return community


def delete_community(db: Session, community: CommunityDB) -> CommunityDB:
    db.delete(community)
    db.commit()
    return community


def add_follower(
    db: Session,
    follower: UserDB,
    community: CommunityDB
):
    community.followers.append(follower)
    db.commit()
    return community



def get_all_followers(
    db: Session,
    limit: int,
    offset: int,
    community_id: int
) -> List[UserDB]:
    return (
        db.query(UserDB)
        .join(UserDB.subscribes)
        .filter(CommunityDB.id == community_id)
        .offset(offset)
        .limit(limit)
        .all()
    )

def delete_follower(
    db: Session,
    follower: UserDB,
    community: CommunityDB        
):
    community.followers.remove(follower)
    db.commit()
    return community


def get_community_posts(
    db: Session,
    community_id: int,
    limit: int,
    offset: int
) -> List[PostDB]:
    return (
        db.query(PostDB)
        .filter(PostDB.community_id == community_id)
        .offset(offset)
        .limit(limit)
        .all()
    )


def is_community_exist_by_name(db: Session, name: str):
    return get_community_by_name(db, name) is not None