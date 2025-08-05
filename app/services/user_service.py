from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import user as user_crud
from app.db.models import (User as UserDB,
                           Community as CommunityDB)
from app.schemas.user import *
from app.schemas.community import Community
from app.core.security import hash_password
from app.core.logging_config import logger
from app.core.log_context import set_user_context 



def get_all_users(
        db: Session,
        limit: int,
        offset: int,
) -> List[User]:
    users = user_crud.get_all_users(db, limit, offset)
    logger.info(
        "users_fetched_from_db",
        total_count=len(users)
    )
    return [User.from_orm(user) for user in users]


def get_user_by_username(
        db: Session,
        username: str
) -> User:
    user = user_crud.get_user_by_username(db, username)

    if not user:
        logger.warning(
            "user_fetch_failed",
            target_user_id=username,
            reason="not_found"
        ) 
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(
        "user_fetched_from_db",
        target_user_id=user.id
    )
    return User.from_orm(user)




def get_user_subscribes(
    db: Session,
    limit: int,
    offset: int,
    user_id: int
) -> List[Community]:
    if not user_crud.get_user_by_id(db, user_id):
        logger.warning(
            "user_subscribes_fetch_faild",
            target_user_id=user_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    logger.info("user_subscribes_fetched_from_db")
    return [Community.from_orm(c) for c in user_crud.get_all_subsribes(db, limit, offset, user_id)]


def get_current_user_subscribes(
    db: Session,
    limit: int,
    offset: int,
    current_user: User
) -> List[Community]:
    set_user_context(current_user)
    
    logger.info("user_subscribes_fetched_from_db")
    return [Community.from_orm(c) for c in user_crud.get_all_subsribes(db, limit, offset, current_user.id)]

    



def create_user(
        db: Session,
        user: UserCreate,
        current_user: User
) -> User:
    set_user_context(current_user)

    if user_crud.is_user_exist(db, user.username):
        logger.warning(
            "user_create_failed",
            target_user_username=user.username,
            reason="already_exist"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User {user.username} has already existed"
        )
    
    if user.role == "admin" and current_user.role != "admin":
        logger.warning(
            "user_create_failed",
            target_user_role=user.role,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permissions to create admin user"
        )

    new_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password),
        avatar_url=user.avatar_url,
        role=user.role
    )

    user_crud.create_user(db, new_user)
    logger.info(
        "user_created",
        target_user_id=new_user.id
    )
    return User.from_orm(new_user)


def update_user(
        db: Session,
        user_id: int,
        updates: UserUpdate,
        current_user: User
) -> User:
    set_user_context(current_user)

    if user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            "user_update_failed",
            target_user_id=user_id,
            reason="permission_denied"
        )
        raise HTTPException(
            status_code=403,
            detail="You do not have permissions to update other users"
        )
    
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        logger.warning(
            "user_update_failed",
            target_user_id=user_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )

    if updates.username is not None:
        if user_crud.is_user_exist(db, updates.username):
            logger.warning(
                "user_update_failed",
                target_user_name=updates.username,
                reason="already_exist"
            )
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
            logger.warning(
                "update_user_failed",
                target_user_id=user_id,
                reason="permission_denied"
            )
            raise HTTPException(
                status_code=403,
                detail="You do not have permissions to set your user as admin"
            )
        user.role = updates.role

    user_crud.update_user(db, user)
    logger.info("user_updated", target_user_id=user_id)
    return User.from_orm(user)

def delete_user(
    db: Session,
    user_id: int,
    current_user: User
) -> dict:
    set_user_context(current_user)

    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        logger.warning(
            "user_delete_failed",
            target_user_id=user_id,
            reason="not_found"
        )
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    if user.username != current_user.username:
        if current_user.role != "admin":
            logger.warning(
                "user_delete_failed",
                target_user_id=user_id,
                reason="permission_denied"
            )
            raise HTTPException(
                status_code=403,
                detail="You do not have permissions to delete other users"
            )
        
    user_crud.delete_user(db, user)
    logger.info(
        "user_deleted",
        target_user_id=user_id
    )
    return {"message": f"User {user.username} has been deleted"}