from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, ForeignKey, Float, Integer, Boolean, JSON, DateTime, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from ..core.models import User as CoreUser, Zone as CoreZone, Role as CoreRole, Operation as CoreOperation
from ..core.models import GammaMapping as CoreGamma, Constraint as CoreConstraint
from ..core.types import ConstraintType
from .base import Storage

Base = declarative_base()

role_operations = Table(
    "role_operations",
    Base.metadata,
    Column("role_id", String, ForeignKey("roles.id")),
    Column("operation_id", String, ForeignKey("operations.id")),
)

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String)
    attributes = Column(JSON)
    is_active = Column(Boolean, default=True)

class ZoneModel(Base):
    __tablename__ = "zones"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(String, ForeignKey("zones.id"))
    description = Column(String)
    parent = relationship("ZoneModel", remote_side=[id], backref="children")

class RoleModel(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=False)
    name = Column(String, nullable=False)
    parent_role_id = Column(String, ForeignKey("roles.id"))
    description = Column(String)
    zone = relationship("ZoneModel", backref="roles")
    parent_role = relationship("RoleModel", remote_side=[id])
    operations = relationship("OperationModel", secondary=role_operations)

class OperationModel(Base):
    __tablename__ = "operations"
    id = Column(String, primary_key=True)
    app_name = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)

class UserZoneRoleModel(Base):
    __tablename__ = "user_zone_roles"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    zone_id = Column(String, ForeignKey("zones.id"), primary_key=True)
    role_id = Column(String, ForeignKey("roles.id"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.now)

class GammaMappingModel(Base):
    __tablename__ = "gamma_mappings"
    child_zone_id = Column(String, ForeignKey("zones.id"), primary_key=True)
    child_role_id = Column(String, ForeignKey("roles.id"), primary_key=True)
    parent_zone_id = Column(String, ForeignKey("zones.id"))
    parent_role_id = Column(String, ForeignKey("roles.id"))
    weight = Column(Float, default=1.0)
    priority = Column(Integer, default=0)

class ConstraintModel(Base):
    __tablename__ = "constraints"
    id = Column(String, primary_key=True)
    type = Column(String)
    target = Column(JSON)
    condition = Column(JSON)
    is_negative = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

class SQLAlchemyStore(Storage):
    def __init__(self, database_url: str, echo: bool = False):
        self.engine = create_engine(database_url, echo=echo, future=True)
        self.Session = sessionmaker(bind=self.engine, future=True)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        Base.metadata.drop_all(self.engine)

    # Converters
    def _to_core_user(self, m: UserModel) -> CoreUser:
        return CoreUser(id=m.id, username=m.username, email=m.email, attributes=m.attributes or {}, is_active=m.is_active)

    def _to_core_zone(self, m: ZoneModel) -> CoreZone:
        return CoreZone(id=m.id, name=m.name, parent_id=m.parent_id, description=m.description or "")

    def _to_core_role(self, m: RoleModel) -> CoreRole:
        return CoreRole(id=m.id, zone_id=m.zone_id, name=m.name, parent_role_id=m.parent_role_id, description=m.description or "", base_permissions={op.id for op in m.operations})

    def _to_core_operation(self, m: OperationModel) -> CoreOperation:
        return CoreOperation(id=m.id, app_name=m.app_name, name=m.name, description=m.description or "")

    def _to_core_constraint(self, m: ConstraintModel) -> CoreConstraint:
        return CoreConstraint(id=m.id, type=ConstraintType(m.type), target=m.target or {}, condition=m.condition or {}, is_negative=m.is_negative, priority=m.priority)

    # Reads
    def get_user(self, user_id: str) -> Optional[CoreUser]:
        with self.Session() as s:
            m = s.get(UserModel, user_id)
            return self._to_core_user(m) if m else None

    def get_zone(self, zone_id: str) -> Optional[CoreZone]:
        with self.Session() as s:
            m = s.get(ZoneModel, zone_id)
            return self._to_core_zone(m) if m else None

    def get_role(self, role_id: str) -> Optional[CoreRole]:
        with self.Session() as s:
            m = s.get(RoleModel, role_id)
            return self._to_core_role(m) if m else None

    def get_operation(self, op_id: str) -> Optional[CoreOperation]:
        with self.Session() as s:
            m = s.get(OperationModel, op_id)
            return self._to_core_operation(m) if m else None

    def get_user_roles(self, user_id: str, zone_id: str) -> List[CoreRole]:
        with self.Session() as s:
            roles = s.query(RoleModel).join(UserZoneRoleModel, UserZoneRoleModel.role_id == RoleModel.id).filter(UserZoneRoleModel.user_id == user_id, RoleModel.zone_id == zone_id).all()
            return [self._to_core_role(m) for m in roles]

    def get_zone_roles(self, zone_id: str) -> List[CoreRole]:
        with self.Session() as s:
            roles = s.query(RoleModel).filter(RoleModel.zone_id == zone_id).all()
            return [self._to_core_role(m) for m in roles]

    def get_zone_children(self, zone_id: str) -> List[CoreZone]:
        with self.Session() as s:
            zs = s.query(ZoneModel).filter(ZoneModel.parent_id == zone_id).all()
            return [self._to_core_zone(m) for m in zs]

    def get_child_roles(self, parent_role_id: str) -> List[CoreRole]:
        with self.Session() as s:
            rs = s.query(RoleModel).filter(RoleModel.parent_role_id == parent_role_id).all()
            return [self._to_core_role(m) for m in rs]

    def get_gamma_mappings(self, child_zone_id: str, child_role_id: str) -> List[CoreGamma]:
        with self.Session() as s:
            ms = s.query(GammaMappingModel).filter(GammaMappingModel.child_zone_id == child_zone_id, GammaMappingModel.child_role_id == child_role_id).all()
            return [CoreGamma(child_zone_id=m.child_zone_id, child_role_id=m.child_role_id, parent_zone_id=m.parent_zone_id, parent_role_id=m.parent_role_id, weight=m.weight, priority=m.priority) for m in ms]

    def get_constraints(self, **filters) -> List[CoreConstraint]:
        with self.Session() as s:
            q = s.query(ConstraintModel)
            for k, v in filters.items():
                if hasattr(ConstraintModel, k):
                    q = q.filter(getattr(ConstraintModel, k) == v)
            ms = q.all()
            return [self._to_core_constraint(m) for m in ms]

    # Writes
    def add_user(self, user: CoreUser) -> None:
        with self.Session() as s:
            s.add(UserModel(id=user.id, username=user.username, email=user.email, attributes=user.attributes, is_active=user.is_active))
            s.commit()

    def add_zone(self, zone: CoreZone) -> None:
        with self.Session() as s:
            s.add(ZoneModel(id=zone.id, name=zone.name, parent_id=zone.parent_id, description=zone.description))
            s.commit()

    def add_role(self, role: CoreRole) -> None:
        with self.Session() as s:
            rm = RoleModel(id=role.id, zone_id=role.zone_id, name=role.name, parent_role_id=role.parent_role_id, description=role.description)
            if role.base_permissions:
                ops = s.query(OperationModel).filter(OperationModel.id.in_(list(role.base_permissions))).all()
                rm.operations = ops
            s.add(rm)
            s.commit()

    def add_operation(self, op: CoreOperation) -> None:
        with self.Session() as s:
            s.add(OperationModel(id=op.id, app_name=op.app_name, name=op.name, description=op.description))
            s.commit()

    def assign_user_to_role(self, user_id: str, zone_id: str, role_id: str) -> None:
        with self.Session() as s:
            s.add(UserZoneRoleModel(user_id=user_id, zone_id=zone_id, role_id=role_id))
            s.commit()
