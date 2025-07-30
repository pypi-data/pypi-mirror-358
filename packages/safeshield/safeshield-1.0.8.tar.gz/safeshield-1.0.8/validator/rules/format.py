from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type
import re
import zoneinfo
import ipaddress
import json
import uuid

# =============================================
# FORMAT VALIDATION RULES
# =============================================

class EmailRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid email address."

class UrlRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(
            r'^(https?:\/\/)?'  # protocol
            r'([\da-z\.-]+)\.'  # domain
            r'([a-z\.]{2,6})'   # top level domain
            r'([\/\w \.-]*)*\/?$',  # path/query
            value
        ))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid URL."

class JsonRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid JSON string."

class UuidRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid UUID."

class UlidRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(r'^[0-9A-HJKMNP-TV-Z]{26}$', value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid ULID."

class IpRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid IP address."

class TimezoneRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        try:
            zoneinfo.ZoneInfo(value)
            return True
        except zoneinfo.ZoneInfoNotFoundError:
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid timezone."

class HexRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not isinstance(value, str):
            return False
        return bool(re.match(r'^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', value))
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a valid hexadecimal color code."
