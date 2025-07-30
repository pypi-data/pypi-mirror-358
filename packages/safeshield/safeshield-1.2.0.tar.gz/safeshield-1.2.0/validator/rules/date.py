from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from datetime import datetime
from dateutil.parser import parse

class DateRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
            
        try:
            parse(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name is not a valid date."

class DateEqualsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return False
        
        value = self.get_field_value(value, value)
        
        try:
            date1 = parse(value)
            
            params[0] = self.get_field_value(params[0], params[0])
            
            date2 = parse(params[0])
            return date1 == date2
        except ValueError as e:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be equal to {params[0]}."
    
class AfterRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
            
        try:
            # Parse input date
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
                
            # Parse comparison date
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value > compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be after {params[0]}"
    
class AfterOrEqualRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
        
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value >= compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be after or equal to {params[0]}"
    
class BeforeRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
        
        value = self.get_field_value(value, value)
    
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params[0] = self.get_field_value(params[0], params[0])    
            compare_date = parse(params[0])
            
            return date_value < compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be before {params[0]}"
    
class BeforeOrEqualRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
        
        value = self.get_field_value(value, value) 
        
        try:
            if isinstance(value, str):
                date_value = parse(value)
            elif isinstance(value, datetime):
                date_value = value
            else:
                return False
            
            params[0] = self.get_field_value(params[0], params[0])
            compare_date = parse(params[0])
            
            return date_value <= compare_date
            
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be before or equal to {params[0]}"
    
class DateFormatRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1 or not isinstance(value, str):
            return False
        
        try:
            datetime.strptime(value, params[0])
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must match the format {params[0]}"