from datetime import time, datetime
from ..core.models import Constraint, User, Role, Zone, Operation
from .base import ConstraintEvaluator

class SoDEvaluator(ConstraintEvaluator):
    def evaluate(self, constraint: Constraint, user: User, role: Role, zone: Zone, operation: Operation, context=None) -> bool:
        target = constraint.target or {}
        if user.id != target.get("user_id", user.id):
            return False
        # Placeholder: real SoD would query conflicting roles/operations
        return False

class TemporalEvaluator(ConstraintEvaluator):
    def evaluate(self, constraint: Constraint, user: User, role: Role, zone: Zone, operation: Operation, context=None) -> bool:
        cond = constraint.condition or {}
        now = datetime.now()
        if "time_range" in cond:
            start, end = cond["time_range"]
            start_t = time.fromisoformat(start)
            end_t = time.fromisoformat(end)
            if not (start_t <= now.time() <= end_t):
                return False
        return True

class AttributeEvaluator(ConstraintEvaluator):
    def evaluate(self, constraint: Constraint, user: User, role: Role, zone: Zone, operation: Operation, context=None) -> bool:
        cond = constraint.condition or {}
        attr = cond.get("attribute")
        op = cond.get("operator")
        val = cond.get("value")
        user_attr = user.attributes.get(attr)
        if op == ">=" and isinstance(user_attr, (int, float)) and user_attr >= val:
            return True
        return False

class ContextEvaluator(ConstraintEvaluator):
    def evaluate(self, constraint: Constraint, user: User, role: Role, zone: Zone, operation: Operation, context=None) -> bool:
        if context is None:
            return False
        cond = constraint.condition or {}
        for k, expected in cond.items():
            if context.get(k) != expected:
                return False
        return True
