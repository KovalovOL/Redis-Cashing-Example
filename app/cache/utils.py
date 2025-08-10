from .redis_client import redis_client
from app.db.models import (Community as CommunityDB,
                           Post as PostDB
                           )
from app.schemas.community import Community
from app.schemas.post import Post


def get_cache(key: str):
    return redis_client.get(key)

def set_cache(key: str, value: str, ttl: int = 120):
    redis_client.set(key, value, ttl)

def delete_cache(key: str):
    redis_client.delete(key)



def serialize_community(community: CommunityDB) -> str:
    return Community.from_orm(community).model_dump_json()


def deserialize_community(data: str) -> Community:
    if not data:
        return None
    try:
        return Community.model_validate_json(data)
    except:
        return None
    

def serialize_post(post: PostDB) -> str:
    return Post.from_orm(post).model_dump_json()


def deserialize_post(data: str) -> Post:
    if not data:
        return None
    try:
        return Post.model_validate_json(data)
    except:
        return None
