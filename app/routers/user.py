from fastapi import APIRouter, Depends, Path, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Literal, Optional

from app.core.dependencies import get_db, get_current_user
from app.crud import user as user_crud
from app.schemas.user import *


router = APIRouter()


@router.get("/", response_model=List[User])
async def get_user(
    id: int = Query(None, ge=0),
    username: str = Query(None, max_length=50),
    role: Optional[Literal["user", "admin"]] = None,
    db: Session = Depends(get_db)
) -> List[User]:
    
    if role or id or username:
        filter = UserFilter(id=id, username=username, role=role)
        return user_crud.get_users_by_conditions(db, filter)
    
    return user_crud.get_all_users(db)


@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    
    if user.role == "admin" and current_user.role != "admin":
        raise HTTPException(status_code=403, detail=f"You are not allowed to create an admin user")

    return user_crud.create_user(db, user)


@router.put("/{user_id}", response_model=User)
async def update_user(
    updates: UserUpdate,
    user_id: int = Path(..., ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)

) -> User:
    
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You have not permission to edit other users")

    return user_crud.update_user(db, user_id, updates)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int = Path(..., ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail=f"You have not permission to delete other users")
    
    return user_crud.delete_user(db, user_id)