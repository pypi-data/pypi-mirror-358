from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
from enum import Enum
# from .string import pascal_to_snake
import inspect
import re

class ValidationRule(ABC):
    """Abstract base class for all validation rules"""
    
    def __init__(self, *params: str):
        self._validator: Optional['Validator'] = None
        self._params: List[str] = list(params)
        
    def __init_subclass__(cls):
        cls.rule_name = cls.pascal_to_snake(cls.__name__)
    
    @property
    def params(self) -> List[str]:
        return self._params
    
    @params.setter
    def params(self, value: List[str]) -> None:
        self._params = value
    
    def set_validator(self, validator: 'Validator') -> None:
        """Set the validator instance this rule belongs to."""
        self._validator = validator
        
    def set_field_exists(self, exists: bool):
        self._field_exists = exists
    
    @property
    def validator(self) -> 'Validator':
        """Get the validator instance."""
        if self._validator is None:
            raise RuntimeError("Validator not set for this rule!")
        return self._validator
    
    @property
    def field_exists(self):
        return self._field_exists
    
    def get_field_value(self, field_name, default=''):
        return str(self.validator.data.get(field_name, default))
    
    @staticmethod
    def is_empty(value):
        return value in (None, '', [], {})
    
    @abstractmethod
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        """Validate a field's value."""
        pass
    
    @abstractmethod
    def message(self, field: str) -> str:
        """Generate an error message if validation fails."""
        pass
    
    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Return the name of the rule for error messages."""
        pass
    
    def _parse_option_values(self, field: str, params: List[str]) -> List[Any]:
        """Parse parameters into allowed values, supporting both Enum class and literal values"""
        if not params:
            raise ValueError(
                f"{self.rule_name} rule requires parameters. "
                f"Use '({self.rule_name}, EnumClass)' or '{self.rule_name}:val1,val2'"
            )
            
        enum_params = [param for param in params if inspect.isclass(param) and issubclass(param, Enum)]
        params = [param for param in params if param not in enum_params]
        
        for enum_param in enum_params:
            params.extend([e.value for e in enum_param])
            
        params = set([str(param) for param in params])
            
        param_str = ' ,'.join(params)
        
        return [v.strip() for v in param_str.split(',') if v.strip()]
    
    def pascal_to_snake(name):
        """Convert PascalCase to snake_case"""
        # Handle kasus khusus terlebih dahulu
        special_cases = {
            'UUIDRule': 'uuid',
            'IPRule': 'ip',
            'URLRule': 'url'
        }
        if name in special_cases:
            return special_cases[name]
        
        # Konversi regular PascalCase ke snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return result.replace('_rule', '')