from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.models import User as UserDB
from app.schemas.user import *
from app.core.security import hash_password


def get_user_by_id(user_id: int, db: Session) -> UserDB:
    return db.query(UserDB).filter(UserDB.id == user_id)

def get_all_users(db: Session) -> List[User]:
    users = db.query(UserDB).all()
    return [User.from_orm(user) for user in users]


def get_users_by_conditions(db: Session, filter: UserFilter) -> List[User]:
    conditions = []

    if filter.username is not None:
        conditions.append(UserDB.username == filter.username)
    if filter.id is not None:
        conditions.append(UserDB.id == filter.id)
    if filter.role is not None:
        conditions.append(UserDB.role == filter.role)
    
    users = db.query(UserDB).filter(*conditions).all()
    return [User.from_orm(user) for user in users]



def create_user(db: Session, user: UserCreate) -> User:
    new_user = UserDB(
        username = user.username,
        hashed_password = hash_password(user.password),
        role = user.role,
        avatar_url = user.avatar_url
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return User.from_orm(new_user)


def update_user(db: Session, user_id: int, updates: UserUpdate) -> User:
    user = db.query(UserDB).filter(UserDB.id == user_id).first() 

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    if updates.username is not None:
        user.username = updates.username
    if updates.password is not None:
        user.hashed_password = hash_password(updates.password)
    if updates.avatar_url is not None:
        user.avatar_url = updates.avatar_url
    if updates.role is not None:
        user.role = updates.role

    db.commit()
    db.refresh(user)

    return User.from_orm(user)

def delete_user(db: Session, user_id: int) -> dict:
    user = db.query(UserDB).filter(UserDB.id == user_id).first() 

    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
    
    db.delete(user)
    db.commit()

    return {"message": f"User {user.username} has been deleted"}


def is_user_exist(db: Session, username: str) -> bool:
    if db.query(UserDB).filter(UserDB.username == username).first():
        return True
    return False
 

