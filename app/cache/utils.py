import json

from .redis_client import redis_client
from app.db.models import Community as CommunityDB
from app.schemas.community import Community


def get_cache(key: str):
    return redis_client.get(key)

def set_cache(key: str, value: str, ttl: int = 120):
    redis_client.set(key, value, ttl)

def delete_cache(key: str):
    redis_client.delete_cache(key)


def serialize_community(community: CommunityDB) -> str:
    return Community.from_orm(community).model_dump_json()


def deserialize_community(data: str) -> Community:
    if not data:
        return None
    try:
        return Community.model_validate_json(data)
    except Exception:
        return None