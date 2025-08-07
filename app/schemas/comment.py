from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class CommentBase(BaseModel):
    text: str = Field(max_length=500)

    model_config = ConfigDict(from_attributes=True)


class CommentCreateInput(CommentBase):
    ...


class CommentCreate(CommentBase):
    post_id: int = Field(gt=0)
    owner_id: int = Field(gt=0)


class Comment(CommentBase):
    id: int = Field(gt=0)
    owner_id: int = Field(gt=0)
    post_id: int = Field(gt=0)
    time_edited: datetime
    is_edited: bool


class CommentUpdate(BaseModel):
    text: Optional[str] = Field(None, max_length=500)