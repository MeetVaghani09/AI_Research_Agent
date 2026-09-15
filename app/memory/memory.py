from collections import defaultdict

from app.config import settings

_memory = defaultdict(list)
_redis = None

if settings.redis_url:
    try:
        import redis
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
        _redis.ping()
    except Exception:
        _redis = None


def save_message(session_id: str, role: str, message: str):
    item = f"{role}: {message}"

    if _redis:
        key = f"chat:{session_id}"
        _redis.rpush(key, item)
        _redis.ltrim(key, -10, -1)
    else:
        _memory[session_id].append(item)
        _memory[session_id] = _memory[session_id][-10:]


def get_history(session_id: str):
    if _redis:
        return _redis.lrange(f"chat:{session_id}", 0, -1)

    return list(_memory[session_id])

def is_redis_connected() -> bool:
    if _redis is None:
        return False

    try:
        return bool(_redis.ping())
    except Exception:
        return False