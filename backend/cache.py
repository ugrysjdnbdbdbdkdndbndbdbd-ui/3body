"""简单内存 TTL 缓存，用于高频读接口以提升响应速度."""
import time
from typing import Any, Optional

_CACHE: dict[str, tuple[Any, float]] = {}


def cache_get(key: str, ttl_seconds: float) -> Optional[Any]:
    """若存在且未过期则返回缓存值，否则返回 None."""
    if key not in _CACHE:
        return None
    val, expires = _CACHE[key]
    if time.monotonic() > expires:
        del _CACHE[key]
        return None
    return val


def cache_set(key: str, value: Any, ttl_seconds: float) -> None:
    """写入缓存，ttl_seconds 秒后过期."""
    _CACHE[key] = (value, time.monotonic() + ttl_seconds)


def cache_delete(key: str) -> None:
    """删除缓存键."""
    _CACHE.pop(key, None)
