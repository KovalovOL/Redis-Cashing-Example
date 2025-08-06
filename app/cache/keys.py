

def user_cache_key(user_id: int) -> str:
    return f"user:{user_id}"

def community_cache_key(community_id: int) -> str:
    return f"com:{community_id}"

def post_cache_key(post_id: int) -> str:
    return f"post:{post_id}"