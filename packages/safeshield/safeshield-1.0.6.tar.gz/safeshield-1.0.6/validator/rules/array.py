from validator.rules.base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

class ArrayRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        
        self._missing_keys = params
        
        if params:
            params = self._parse_option_values(self.rule_name, params)
            if not isinstance(value, dict):
                return False

            missing = [param for param in params if param not in value]
            self._missing_keys = missing
            return len(missing) == 0

        return isinstance(value, (list, tuple, set))

    def message(self, field: str, params: List[str]) -> str:
        if params:
            return f"The {field} must contain the keys: {', '.join(self._missing_keys)}."
        return f"The {field} must be an array."

class ContainsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        search_value = params[0]
        
        # String contains substring
        if isinstance(value, str):
            return search_value in value
            
        # Array contains element
        if isinstance(value, (list, tuple, set)):
            return search_value in value
            
        # Dictionary contains key
        if isinstance(value, dict):
            return search_value in value.keys()
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must contain {params[0]}"
    
class DistinctRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, (list, tuple, set)):
            return False
            
        return len(value) == len(set(value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must contain unique values"
    
class InArrayRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        return str(value) in params
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be one of: {', '.join(params)}"
    
class InArrayKeysRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, dict):
            return False
            
        return any(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must contain at least one of these keys: {', '.join(params)}"