from validator.rules.base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from datetime import datetime

# =============================================
# TYPE DATA VALIDATION RULES
# =============================================

class NumericRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, (int, float)):
            return True
        if not isinstance(value, str):
            return False
        return value.replace('.', '', 1).isdigit()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a number."

class IntegerRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, int):
            return True
        if not isinstance(value, str):
            return False
        return value.isdigit()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be an integer."

class BooleanRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']
        if isinstance(value, int):
            return value in [0, 1]
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be true or false."
