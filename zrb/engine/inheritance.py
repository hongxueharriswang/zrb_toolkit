from typing import Set, List
from ..core.models import Role
from ..storage.base import Storage

class InheritanceResolver:
    def __init__(self, storage: Storage):
        self.storage = storage

    def get_junior_roles(self, role_id: str, zone_id: str) -> List[Role]:
        result: List[Role] = []
        to_process = [role_id]
        seen = set()
        while to_process:
            current = to_process.pop()
            if current in seen:
                continue
            seen.add(current)
            role = self.storage.get_role(current)
            if role and role.zone_id == zone_id:
                result.append(role)
                children = self.storage.get_child_roles(current)
                to_process.extend([c.id for c in children])
        return result

    def _gamma_inherit(self, role_id: str, zone_id: str) -> Set[str]:
        perms: Set[str] = set()
        mappings = self.storage.get_gamma_mappings(zone_id, role_id)
        mappings = sorted(mappings, key=lambda g: g.priority)
        for gm in mappings:
            parent_role = self.storage.get_role(gm.parent_role_id)
            if parent_role:
                parent_perms = self.compute_effective_permissions(parent_role.id, gm.parent_zone_id)
                perms.update(parent_perms)
        return perms

    def compute_effective_permissions(self, role_id: str, zone_id: str) -> Set[str]:
        role = self.storage.get_role(role_id)
        if not role:
            return set()
        perms: Set[str] = set()
        for jr in self.get_junior_roles(role_id, zone_id):
            perms.update(jr.base_permissions)
        perms.update(self._gamma_inherit(role_id, zone_id))
        return perms
