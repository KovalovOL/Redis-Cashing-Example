from sqlalchemy.orm import Session
from typing import List

from app.db.models import (User as UserDB,
                           Community as CommunityDB)
from app.schemas.user import UserCreate, UserFilter, UserUpdate


def get_all_users(
        db: Session,
        limit: int,
        offset: int
) -> List[UserDB]:
    return db.query(UserDB).offset(offset).limit(limit).all()


def get_user_by_id(db: Session, user_id: int) -> UserDB:
    return db.query(UserDB).filter(UserDB.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> UserDB:
    return db.query(UserDB).filter(UserDB.username == username).first()

def get_user_by_conditions(db: Session, filters: UserFilter) -> List[UserDB]:
    conditions = []

    if filters.id is not None:
        conditions.append(UserDB.id == filters.id)

    if filters.username is not None:
        conditions.append(UserDB.username == filters.username)
        
    if filters.role is not None:
        conditions.append(UserDB.role == filters.role)

    return db.query(UserDB).filter(*conditions).all()


def get_all_subsribes(
    db: Session,
    limit: int,
    offset: int,
    user_id: int
) -> List[CommunityDB]:
    return (
        db.query(CommunityDB)
        .join(CommunityDB.followers)
        .filter(UserDB.id == user_id)
        .offset(offset)
        .limit(limit)
        .all()
    )



def create_user(db: Session, user: UserCreate) -> UserDB:
    new_user = UserDB(
        username=user.username,
        hashed_password=user.password,
        avatar_url=user.avatar_url,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, user: UserDB) -> UserDB:
    db.commit()
    db.refresh(user)
    return user
    
    

def delete_user(db: Session, user: UserDB) -> UserDB:
    db.delete(user)
    db.commit()
    return user
    
 
def is_user_exist(db: Session, username: str):
    user = get_user_by_username(db, username)
    if user:
        return True
    return False
