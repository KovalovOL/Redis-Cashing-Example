from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str = Field(max_length=50)
    text: str = Field(max_length=500)
    community_id: int = Field(gt=0)

    model_config = ConfigDict(from_attributes=True)

class PostCreateInput(PostBase):
    ...


class PostCreate(PostBase):
    owner_id: int = Field(gl=0)


class Post(PostBase):
    id: int
    owner_id: int = Field(gl=0)
    time_edited: datetime
    is_edited: bool


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=50)
    text: Optional[str] = Field(None, max_length=500)
