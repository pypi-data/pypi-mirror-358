from validator.rules.base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import re

# =============================================
# STRING VALIDATION RULES
# =============================================

class StringRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a string."

class AlphaRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value.isalpha()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name may only contain letters."

class AlphaDashRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and bool(re.match(r'^[a-zA-Z0-9_-]+$', value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name may only contain letters, numbers, dashes and underscores."

class AlphaNumRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value.isalnum()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name may only contain letters and numbers."

class UppercaseRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value == value.upper()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be uppercase."

class LowercaseRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and value == value.lower()
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be lowercase."

class AsciiRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return isinstance(value, str) and all(ord(c) < 128 for c in value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must only contain ASCII characters."
    
class StartsWithRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return any(value.startswith(p) for p in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must start with one of the following: {', '.join(params)}."

class EndsWithRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return any(value.endswith(p) for p in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must end with one of the following: {', '.join(params)}."
