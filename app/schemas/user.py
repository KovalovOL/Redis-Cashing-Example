from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    avatar_url: Optional[str] = None
    role: Literal["user", "admin"]

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    username: str = Field(max_length=50)
    password: str = Field(min_length=6)


class User(UserBase):
    id: int = Field(ge=0)


class UserFilter(BaseModel):
    id: Optional[int] = Field(None, ge=0)
    username: Optional[str] = Field(None, max_length=50)
    role: Optional[Literal["user", "admin"]] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[Literal["user", "admin"]] = None


