from cachetools import TTLCache
from typing import Optional, Set, Tuple

class PermissionCache:
    def __init__(self, maxsize: int = 10000, ttl: int = 300):
        self.cache: TTLCache[Tuple[str, str], Set[str]] = TTLCache(maxsize=maxsize, ttl=ttl)

    def get_effective_permissions(self, role_id: str, zone_id: str) -> Optional[Set[str]]:
        return self.cache.get((role_id, zone_id))

    def set_effective_permissions(self, role_id: str, zone_id: str, perms: Set[str]) -> None:
        self.cache[(role_id, zone_id)] = perms

    def invalidate_role(self, role_id: str, zone_id: Optional[str] = None) -> None:
        keys = [k for k in self.cache if k[0] == role_id and (zone_id is None or k[1] == zone_id)]
        for k in keys:
            del self.cache[k]
