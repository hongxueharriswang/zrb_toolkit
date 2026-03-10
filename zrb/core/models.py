from datetime import datetime
from typing import Optional, Set, Dict, Any
from pydantic import BaseModel, Field
from .types import ConstraintType

class User(BaseModel):
    id: str
    username: str
    email: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class Operation(BaseModel):
    id: str
    app_name: str
    name: str
    description: str = ""

class Zone(BaseModel):
    id: str
    name: str
    parent_id: Optional[str] = None
    description: str = ""

class Role(BaseModel):
    id: str
    zone_id: str
    name: str
    parent_role_id: Optional[str] = None
    description: str = ""
    base_permissions: Set[str] = Field(default_factory=set)  # operation ids

class UserZoneRole(BaseModel):
    user_id: str
    zone_id: str
    role_id: str
    assigned_at: datetime = Field(default_factory=datetime.now)

class GammaMapping(BaseModel):
    child_zone_id: str
    child_role_id: str
    parent_zone_id: str
    parent_role_id: str
    weight: float = 1.0
    priority: int = 0

class Constraint(BaseModel):
    id: str
    type: ConstraintType
    target: Dict[str, Any]
    condition: Dict[str, Any]
    is_negative: bool = True
    priority: int = 0
