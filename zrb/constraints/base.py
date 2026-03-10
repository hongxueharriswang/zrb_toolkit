from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..core.models import User, Role, Zone, Operation, Constraint

class ConstraintEvaluator(ABC):
    @abstractmethod
    def evaluate(self, constraint: Constraint, user: User, role: Role, zone: Zone, operation: Operation, context: Optional[Dict] = None) -> bool: ...
