from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from enum import Enum
import re
import inspect
from collections.abc import Iterable

# =============================================
# CONDITIONAL VALIDATION RULES
# =============================================

class RequiredIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2 or len(params) % 2 != 0:
            return True
            
        conditions = list(zip(params[::2], params[1::2]))
        
        condition_met = False
        for other_field, expected_value in conditions:
            if not other_field or expected_value is None:
                continue
                
            actual_value = self.get_field_value(other_field, '')
            if actual_value == expected_value:
                condition_met = True
                break
        
        if not condition_met:
            return True
            
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        valid_conditions = []
        if len(params) >= 2 and len(params) % 2 == 0:
            valid_conditions = [
                f"{params[i]} = {params[i+1]}" 
                for i in range(0, len(params), 2) 
                if params[i] and params[i+1] is not None
            ]
        
        if not valid_conditions:
            return f"Invalid required_if rule configuration for {field}"
            
        return f"The :name field is required when any of these are true: {', '.join(valid_conditions)}"
    
class RequiredAllIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        conditions = [(f.strip(), v.strip()) for f, v in zip(params[::2], params[1::2])]
        
        all_conditions_met = all(
            self.get_field_value(f) == v 
            for f, v in conditions
        )
        
        if not all_conditions_met:
            return True
            
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        conditions = " AND ".join(f"{f} = {v}" for f, v in zip(params[::2], params[1::2]))
        return f"The :name field is required when ALL conditions are met: {conditions}"

class RequiredUnlessRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return not self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required unless {params[0]} is {params[1]}."

class RequiredWithRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if any(f in self.validator.data for f in params):
            return not self.is_empty(value)
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required when {', '.join(params)} is present."

class RequiredWithAllRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if all(f in self.validator.data for f in params):
            return not self.is_empty(value)
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required when all of {', '.join(params)} are present."

class RequiredWithoutRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if any(f not in self.validator.data for f in params):
            return not self.is_empty(value)
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required when {', '.join(params)} is not present."

class RequiredWithoutAllRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        if all(f not in self.validator.data for f in params):
            return not self.is_empty(value)
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is required when none of {', '.join(params)} are present."

class ProhibitedIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '')
        
        if actual_value != other_value:
            return True
            
        return self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is prohibited when {params[0]} is {params[1]}."

class ProhibitedUnlessRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '') 
        
        if actual_value == other_value:
            return True
            
        return self.is_empty(value)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field is prohibited unless {params[0]} is {params[1]}."

class FilledIfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2:
            return False
            
        other_field, other_value = params[0], params[1]
        actual_value = self.get_field_value(other_field, '')
        
        if actual_value != other_value:
            return True
            
        return value not in ('', None)
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name field must be filled when {params[0]} is {params[1]}."

class RegexRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return False
        try:
            return bool(re.fullmatch(params[0], value))
        except re.error:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name format is invalid."

class NotRegexRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return True
        print(not bool(re.search(params[0], value)))
        try:
            return not bool(re.search(params[0], value))
        except re.error:
            return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name format is invalid."

class InRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        allowed_values = self._parse_option_values(field, params)
        return (str(value) in allowed_values or value in allowed_values)

    def message(self, field: str, params: List[str]) -> str:
        allowed_values = self._parse_option_values(field, params)
        return f"The selected :name must be in : {', '.join(map(str, allowed_values))}"

class NotInRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        not_allowed_values = self._parse_option_values(field, params)
        return str(value) not in not_allowed_values
    
    def message(self, field: str, params: List[str]) -> str:
        not_allowed_values = self._parse_option_values(field, params)
        return f"The selected :name must be not in : {', '.join(map(str, not_allowed_values))}"
    
class EnumRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        allowed_values = self._parse_option_values(field, params)
        return (str(value) in allowed_values or value in allowed_values)

    def message(self, field: str, params: List[str]) -> str:
        allowed_values = self._parse_option_values(field, params)
        return f"The :name must be one of: {', '.join(map(str, allowed_values))}"

class UniqueRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not hasattr(self.validator, 'db_manager') or not self.validator.db_manager:
            return False
            
        table = params[0]
        column = field if len(params) == 1 else params[1]
        
        try:
            # Optional: handle ignore case (id)
            ignore_id = None
            if len(params) > 2 and params[2].startswith('ignore:'):
                ignore_field = params[2].split(':')[1]
                ignore_id = self.get_field_value(ignore_field) 
            return self.validator.db_manager.is_unique(table, column, value, ignore_id)
        except Exception as e:
            print(f"Database error in UniqueRule: {e}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name has already been taken."

class ExistsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not hasattr(self.validator, 'db_manager') or not self.validator.db_manager:
            return False
            
        table = params[0]
        column = field if len(params) == 1 else params[1]
        
        try:
            return self.validator.db_manager.exists(table, column, value)
        except Exception as e:
            print(f"Database error in ExistsRule: {e}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The selected :name is invalid."

class ConfirmedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        confirmation_field = f"{field}_confirmation"
        
        return value == self.get_field_value(confirmation_field, '') 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name confirmation does not match."

class SameRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value == self.get_field_value(params[0]) 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name and {params[0]} must match."

class DifferentRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
        return value != self.get_field_value(params[0]) 
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name and {params[0]} must be different."

class AcceptedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, str):
            return value.lower() in ['yes', 'on', '1', 'true']
        if isinstance(value, int):
            return value == 1
        if isinstance(value, bool):
            return value
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be accepted."

class DeclinedRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if isinstance(value, str):
            return value.lower() in ['no', 'off', '0', 'false']
        if isinstance(value, int):
            return value == 0
        if isinstance(value, bool):
            return not value
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be declined."


class BailRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        self.validator._stop_on_first_failure = True
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return ""