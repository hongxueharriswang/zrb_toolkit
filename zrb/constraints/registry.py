from typing import Dict
from ..core.models import Constraint
from ..core.types import ConstraintType
from .base import ConstraintEvaluator
from .evaluators import SoDEvaluator, TemporalEvaluator, AttributeEvaluator, ContextEvaluator

class ConstraintRegistry:
    def __init__(self):
        self._evaluators: Dict[ConstraintType, ConstraintEvaluator] = {
            ConstraintType.SOD: SoDEvaluator(),
            ConstraintType.TEMPORAL: TemporalEvaluator(),
            ConstraintType.ATTRIBUTE: AttributeEvaluator(),
            ConstraintType.CONTEXT: ContextEvaluator(),
        }

    def evaluate(self, constraint: Constraint, *args, **kwargs) -> bool:
        evaluator = self._evaluators.get(constraint.type)
        if evaluator:
            return evaluator.evaluate(constraint, *args, **kwargs)
        return False
