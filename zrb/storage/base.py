from abc import ABC, abstractmethod
from typing import Optional, List
from ..core.models import User, Zone, Role, Operation, UserZoneRole, GammaMapping, Constraint

class Storage(ABC):
    # Reads
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]: ...

    @abstractmethod
    def get_zone(self, zone_id: str) -> Optional[Zone]: ...

    @abstractmethod
    def get_role(self, role_id: str) -> Optional[Role]: ...

    @abstractmethod
    def get_operation(self, op_id: str) -> Optional[Operation]: ...

    @abstractmethod
    def get_user_roles(self, user_id: str, zone_id: str) -> List[Role]: ...

    @abstractmethod
    def get_zone_roles(self, zone_id: str) -> List[Role]: ...

    @abstractmethod
    def get_zone_children(self, zone_id: str) -> List[Zone]: ...

    @abstractmethod
    def get_child_roles(self, parent_role_id: str) -> List[Role]: ...

    @abstractmethod
    def get_gamma_mappings(self, child_zone_id: str, child_role_id: str) -> List[GammaMapping]: ...

    @abstractmethod
    def get_constraints(self, **filters) -> List[Constraint]: ...

    # Writes (minimal)
    @abstractmethod
    def add_user(self, user: User) -> None: ...

    @abstractmethod
    def add_zone(self, zone: Zone) -> None: ...

    @abstractmethod
    def add_role(self, role: Role) -> None: ...

    @abstractmethod
    def add_operation(self, op: Operation) -> None: ...

    @abstractmethod
    def assign_user_to_role(self, user_id: str, zone_id: str, role_id: str) -> None: ...
