from .redis_client import redis_client


def get_cache(key: str):
    return redis_client.get(key)

def set_cache(key: str, value: str, ttl: int = 120):
    redis_client.set(key, value, ttl)

def delete_cache(key: str):
    redis_client.delete_cache(key)