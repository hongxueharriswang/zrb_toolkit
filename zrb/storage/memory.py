from typing import Optional, List, Dict
from ..core.models import User, Zone, Role, Operation, UserZoneRole, GammaMapping, Constraint
from .base import Storage

class MemoryStore(Storage):
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.zones: Dict[str, Zone] = {}
        self.roles: Dict[str, Role] = {}
        self.operations: Dict[str, Operation] = {}
        self.uzr: List[UserZoneRole] = []
        self.gammas: List[GammaMapping] = []
        self.constraints: List[Constraint] = []

    # Reads
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_zone(self, zone_id: str) -> Optional[Zone]:
        return self.zones.get(zone_id)

    def get_role(self, role_id: str) -> Optional[Role]:
        return self.roles.get(role_id)

    def get_operation(self, op_id: str) -> Optional[Operation]:
        return self.operations.get(op_id)

    def get_user_roles(self, user_id: str, zone_id: str) -> List[Role]:
        role_ids = [x.role_id for x in self.uzr if x.user_id == user_id and x.zone_id == zone_id]
        return [self.roles[rid] for rid in role_ids if rid in self.roles]

    def get_zone_roles(self, zone_id: str) -> List[Role]:
        return [r for r in self.roles.values() if r.zone_id == zone_id]

    def get_zone_children(self, zone_id: str) -> List[Zone]:
        return [z for z in self.zones.values() if z.parent_id == zone_id]

    def get_child_roles(self, parent_role_id: str) -> List[Role]:
        return [r for r in self.roles.values() if r.parent_role_id == parent_role_id]

    def get_gamma_mappings(self, child_zone_id: str, child_role_id: str) -> List[GammaMapping]:
        return [g for g in self.gammas if g.child_zone_id == child_zone_id and g.child_role_id == child_role_id]

    def get_constraints(self, **filters) -> List[Constraint]:
        res = self.constraints
        for k, v in filters.items():
            res = [c for c in res if getattr(c, k) == v]
        return list(res)

    # Writes
    def add_user(self, user: User) -> None:
        self.users[user.id] = user

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.id] = zone

    def add_role(self, role: Role) -> None:
        self.roles[role.id] = role

    def add_operation(self, op: Operation) -> None:
        self.operations[op.id] = op

    def assign_user_to_role(self, user_id: str, zone_id: str, role_id: str) -> None:
        self.uzr.append(UserZoneRole(user_id=user_id, zone_id=zone_id, role_id=role_id))
