from validator.rules.base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

# =============================================
# BASIC VALIDATION RULES
# =============================================

class RequiredRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required."

class NullableRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name may be null."

class FilledRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value not in ('', None)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must have a value."

class PresentRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return field in self.validator.data
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be present."

class SometimesRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""
