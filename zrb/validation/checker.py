from typing import List, Set
from ..storage.base import Storage

# Simple structural validations; extend as needed

def validate_config(store: Storage) -> List[str]:
    errors: List[str] = []
    # TODO: add cycle checks, orphan checks, etc.
    return errors
