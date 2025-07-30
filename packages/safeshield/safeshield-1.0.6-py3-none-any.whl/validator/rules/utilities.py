from validator.rules.base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

class AnyOfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return any(self.get_field_value(param, param) == value for param in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be one of: {', '.join(params)}"

class ExcludeRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return False  # This rule is typically used to exclude fields from validation
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is excluded."

class ExcludeIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        conditions = [(f.strip(), v.strip()) for f, v in zip(params[::2], params[1::2])]
        
        all_conditions_met = all(
            self.get_field_value(f) == v 
            for f, v in conditions
        )
        
        if all_conditions_met:
            self.validator._is_exclude = True
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is excluded when {params[0]} is {params[1]}."

class ExcludeUnlessRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        conditions = [(f.strip(), v.strip()) for f, v in zip(params[::2], params[1::2])]
        
        all_conditions_met = all(
            self.get_field_value(f) == v 
            for f, v in conditions
        )
        
        if not all_conditions_met:
            self.validator._is_exclude = True
            
        return True
            
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is excluded unless {params[0]} is {params[1]}."

class ExcludeWithRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(not self.is_empty(self.get_field_value(param, None)) for param in params):
            self.validator._is_exclude = True
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is excluded when any of {', '.join(params)} is present."

class ExcludeWithoutRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if any(self.is_empty(self.get_field_value(param, None)) for param in params):
            self.validator._is_exclude = True
            
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is excluded when any of {', '.join(params)} is missing."

class MissingRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        return value is None
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be missing."

class MissingIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        return value is None if self.get_field_value(other_field, None) == other_value else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be missing when {params[0]} is {params[1]}."

class MissingUnlessRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        return value is None if self.get_field_value(other_field, None) != other_value else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be missing unless {params[0]} is {params[1]}."

class MissingWithRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value is None if any(self.get_field_value(param, None) is not None for param in params) else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be missing when any of {', '.join(params)} is present."

class MissingWithAllRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value is None if all(self.get_field_value(param, None) is not None for param in params) else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be missing when all of {', '.join(params)} are present."

class PresentIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        return value is not None if self.get_field_value(other_field, None) == other_value else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be present when {params[0]} is {params[1]}."

class PresentUnlessRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
        other_field, other_value = params[0], params[1]
        return value is not None if self.get_field_value(other_field, None) != other_value else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be present unless {params[0]} is {params[1]}."

class PresentWithRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value is not None if any(self.get_field_value(param, None) is not None for param in params) else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be present when any of {', '.join(params)} is present."

class PresentWithAllRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value is not None if all(self.get_field_value(param, None) is not None for param in params) else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be present when all of {', '.join(params)} are present."

class ProhibitedIfAcceptedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        other_field = params[0]
        return value is None if self.get_field_value(other_field, None) in ['yes', 'on', '1', 1, True, 'true', 'True'] else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is prohibited when {params[0]} is accepted."

class ProhibitedIfDeclinedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        other_field = params[0]
        return value is None if self.get_field_value(other_field, None) in ['no', 'off', '0', 0, False, 'false', 'False'] else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is prohibited when {params[0]} is declined."

class ProhibitsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or value is None:
            return True
        return all(self.get_field_value(param, param) in (None, 'None') for param in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"When :name is present, {', '.join(params)} must be absent."

class RequiredIfAcceptedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        other_field = params[0]
        return value is not None if self.get_field_value(other_field, None) in ['yes', 'on', '1', 1, True, 'true', 'True'] else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required when {params[0]} is accepted."

class RequiredIfDeclinedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        other_field = params[0]
        return value is not None if self.get_field_value(other_field, other_field) in ['no', 'off', '0', 0, False, 'false', 'False'] else True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required when {params[0]} is declined."

class RequiredArrayKeysRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, dict) or not params:
            return False
        return all(key in value for key in params)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must contain all required keys: {', '.join(params)}"