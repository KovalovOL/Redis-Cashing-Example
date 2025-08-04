from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from app.core.security import hash_password, create_access_token, verify_password
from app.schemas.user import UserCreate, User, UserLogin
from app.crud import user as user_crud
from app.core.logging_config import logger


def register_user(
    user:  UserCreate,
    db: Session
) -> User:
    if user_crud.is_user_exist(db, user.username):
        logger.warning(
            "user_register_failed",
            username=user.username,
            reason="already_exist"
        )
        raise HTTPException(
            status_code=409,
            detail="This username already exist"
        )
    
    user_data = UserCreate(
        username=user.username,
        password=hash_password(user.password),
        avatar_url=user.avatar_url,
        role="user"
    )

    logger.info("user_registered", target_user_id=user_data.id)
    created_user = user_crud.create_user(db, user_data)
    return User.from_orm(created_user)



def login_user(
    user: UserLogin,
    response: Response,
    db: Session
) -> dict:
    
    user_data = user_crud.get_user_by_username(db, user.username)
    if not user_data or not verify_password(user.password, user_data.hashed_password):
        logger.warning(
            "user_login_failed",
            reason="incorrect_data",
            user_id=user_data.id
        )
        raise HTTPException(
            status_code=401,
            detail="Incorrect password or username"
        )
    
    token_data = {"sub": user_data.username, "role": user_data.role}
    token = create_access_token(token_data)
    response.set_cookie("access_token", token, httponly=True)

    logger.info("user_login_success", user_id=user_data.id)
    return {
        "username": user_data.username,
        "access_token": token 
    }