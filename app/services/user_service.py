from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import user as user_crud
from app.db.models import User as UserDB
from app.schemas.user import *
from app.core.security import hash_password


def get_all_users(db: Session) -> List[User]:
    users = user_crud.get_all_users(db)
    return [User.from_orm(user) for user in users]


def get_user_by_username(db: Session, username: str) -> User:
    user = user_crud.get_user_by_username(db, username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User.from_orm(user)


def create_user(db: Session, user: UserCreate, current_user: User) -> User:
    if user_crud.is_user_exist(db, user.username):
        raise HTTPException(
            status_code=409,
            detail=f"User {user.username} has already existed"
        )
    
    if user.role == "admin" and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permissions to create an admin users"
        )

    new_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password),
        avatar_url=user.avatar_url,
        role=user.role
    )

    user_crud.create_user(db, new_user)
    return User.from_orm(new_user)


def update_user(
        db: Session,
        user_id: int,
        updates: UserUpdate,
        current_user: User
) -> User:
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permissions to update other users"
        )
    
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )

    if updates.username is not None:
        if user_crud.is_user_exist(db, updates.username):
            raise HTTPException(
                status_code=403,
                detail=f"User {updates.username} has already existed"
            )
        user.username = updates.username

    if updates.password is not None:
        user.hashed_password = hash_password(updates.password)

    if updates.avatar_url is not None:
        user.avatar_url = updates.avatar_url

    if updates.role is not None:
        if updates.role == "admin" and current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="You do not have permissions to set your user as admin"
            )
        user.role = updates.role

    user_crud.update_user(db, user)
    return User.from_orm(user)

def delete_user(
    db: Session,
    user_id: int,
    current_user: User
) -> User:
    
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    if user.username != current_user.username:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403,
                detail="You do not have permissions to delete other users"
            )
        
    user_crud.delete_user(db, user)
    return {"message": f"User {user.username} has been deleted"}