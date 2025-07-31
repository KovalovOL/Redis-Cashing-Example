from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class CommunityBase(BaseModel):
    community_name: str = Field(max_length=50)
    description: str = Field(max_length=500)
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommunityCreate(CommunityBase):
    owner_id: int = Field(ge=0)


class Community(CommunityBase):
    id: int
    owner_id: int = Field(ge=0)


class CommunityFilter(BaseModel):
    id: Optional[int] = None
    community_name: Optional[str] = Field(None, max_length=50)
    owner_id: Optional[int] = Field(None, ge=0)


class CommunityUpdate(BaseModel):
    community_name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    photo_url: Optional[str] = None
