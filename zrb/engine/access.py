from typing import Optional, Set, Union
from ..core.models import User, Operation, Zone, Role
from ..core.types import AccessMode
from ..storage.base import Storage
from ..constraints.registry import ConstraintRegistry
from .inheritance import InheritanceResolver
from .cache import PermissionCache

class AccessEngine:
    def __init__(self, storage: Storage, cache_ttl: int = 300):
        self.storage = storage
        self.resolver = InheritanceResolver(storage)
        self.cache = PermissionCache(ttl=cache_ttl)
        self.constraint_registry = ConstraintRegistry()

    def _normalize_mode(self, mode: Union[AccessMode, str]) -> AccessMode:
        if isinstance(mode, str):
            try:
                return AccessMode(mode)
            except Exception:
                return AccessMode.INFERENTIAL
        return mode

    def _get_effective_permissions(self, role_id: str, zone_id: str, mode: AccessMode) -> Set[str]:
        if mode == AccessMode.DIRECT:
            role = self.storage.get_role(role_id)
            return role.base_permissions if role else set()
        cached = self.cache.get_effective_permissions(role_id, zone_id)
        if cached is not None:
            return cached
        perms = self.resolver.compute_effective_permissions(role_id, zone_id)
        self.cache.set_effective_permissions(role_id, zone_id, perms)
        return perms

    def decide(
        self,
        user: User,
        operation: Operation,
        zone: Zone,
        mode: Union[AccessMode, str] = AccessMode.INFERENTIAL,
        context: Optional[dict] = None,
    ) -> bool:
        mode = self._normalize_mode(mode)
        if not user.is_active:
            return False
        roles = self.storage.get_user_roles(user.id, zone.id)
        if not roles:
            return False
        allowed_by_role = False
        for role in roles:
            perms = self._get_effective_permissions(role.id, zone.id, mode)
            if operation.id in perms:
                allowed_by_role = True
                break
        if not allowed_by_role:
            return False
        # Constraints evaluation (negative constraints deny)
        constraints = self.storage.get_constraints()
        for constr in constraints:
            if self.constraint_registry.evaluate(constr, user, role, zone, operation, context):
                if constr.is_negative:
                    return False
        return True
