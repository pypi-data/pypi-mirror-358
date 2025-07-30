from validator.rules.base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

# =============================================
# COMPARISON VALIDATION RULES
# =============================================

class MinRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        try:
            min_val = float(params[0])
        except ValueError:
            return False
            
        if isinstance(value, (int, float)):
            return value >= min_val
        elif isinstance(value, str):
            try:
                return len(value) >= min_val
            except ValueError:
                return len(value) >= min_val
        elif isinstance(value, (list, dict, set)):
            return len(value) >= min_val
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be at least {params[0]}."

class MaxRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
            
        try:
            max_val = float(params[0])
            
            # Handle Werkzeug/Flask FileStorage
            if hasattr(value, 'content_length'):  # Flask/Werkzeug
                file_size = value.content_length
                print(f"File size (content_length): {file_size}")
                return file_size <= max_val
                
            # Handle generic file objects with size attribute
            if hasattr(value, 'size'):
                file_size = value.size
                return file_size <= max_val
                
            # Handle file-like objects with seek/read
            if hasattr(value, 'seek') and hasattr(value, 'read'):
                try:
                    current_pos = value.tell()
                    value.seek(0, 2)  # Seek to end
                    file_size = value.tell()
                    value.seek(current_pos)  # Return to original position
                    return file_size <= max_val
                except (AttributeError, IOError):
                    pass

            # Numeric validation
            if isinstance(value, (int, float)):
                return value <= max_val
                
            # String/collection length validation
            if isinstance(value, (str, list, dict, set, tuple)):
                length = len(value)
                return length <= max_val
                
            # String numeric validation
            if isinstance(value, str):
                try:
                    num = float(value)
                    return num <= max_val
                except ValueError:
                    length = len(value)
                    return length <= max_val
                    
        except (ValueError, TypeError) as e:
            return False
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        value = self.get_field_value(field)
        if value is None:
            return f"The {field} must not exceed {params[0]}"
            
        # Check all possible file size attributes
        file_attrs = ['content_length', 'size', 'fileno']
        if any(hasattr(value, attr) for attr in file_attrs):
            return f"File {field} must not exceed {params[0]} bytes"
        return f"The {field} must not exceed {params[0]}"

class BetweenRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) != 2:
            return False
            
        try:
            min_val = float(params[0])
            max_val = float(params[1])
            
            # File size validation (untuk Werkzeug/FileStorage)
            if hasattr(value, 'content_length'):  # Cek atribut Werkzeug
                file_size = value.content_length
                return min_val <= file_size <= max_val
            elif hasattr(value, 'size'):  # Cek atribut umum
                file_size = value.size
                return min_val <= file_size <= max_val
                
            # Numeric validation
            if isinstance(value, (int, float)):
                return min_val <= value <= max_val
                
            # String/collection length validation
            if isinstance(value, (str, list, dict, set, tuple)):
                length = len(value)
                return min_val <= length <= max_val
                
            # String numeric validation
            if isinstance(value, str):
                try:
                    num = float(value)
                    return min_val <= num <= max_val
                except ValueError:
                    length = len(value)
                    return min_val <= length <= max_val
                    
        except (ValueError, TypeError) as e:
            return False
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        value = self.get_field_value(field)
        if hasattr(value, 'content_length') or hasattr(value, 'size'):
            return f"File {field} must be between {params[0]} and {params[1]} bytes"
        return f"The {field} must be between {params[0]} and {params[1]}"

class SizeRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or len(params) < 1:
            return False
            
        try:
            target_size = float(params[0])
            
            # 1. Handle file objects (Flask/Werkzeug/FastAPI)
            if hasattr(value, 'content_length'):  # Flask/Werkzeug
                return value.content_length == target_size
            elif hasattr(value, 'size'):  # FastAPI or custom file objects
                return value.size == target_size
            elif hasattr(value, 'seek') and hasattr(value, 'tell'):  # File-like objects
                current_pos = value.tell()
                value.seek(0, 2)  # Seek to end
                file_size = value.tell()
                value.seek(current_pos)  # Return to original position
                return file_size == target_size
                
            # 2. Handle numeric values
            if isinstance(value, (int, float)):
                return value == target_size
                
            # 3. Handle strings and collections
            if isinstance(value, (str, list, dict, set, tuple)):
                return len(value) == target_size
                
            # 4. Handle string representations of numbers
            if isinstance(value, str):
                try:
                    return float(value) == target_size
                except ValueError:
                    return len(value) == target_size
                    
        except (ValueError, TypeError, AttributeError) as e:
            return False
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        value = self.get_field_value(field)
        if value is None:
            return f"The {field} must be exactly {params[0]}"
            
        # Check for file attributes
        file_attrs = ['content_length', 'size', 'fileno']
        if any(hasattr(value, attr) for attr in file_attrs):
            return f"File {field} must be exactly {params[0]} bytes"
            
        return f"The {field} must be exactly {params[0]}"
    
class DigitsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params or not isinstance(value, str):
            return False
            
        try:
            digits = int(params[0])
        except ValueError:
            return False
            
        return value.isdigit() and len(value) == digits
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be {params[0]} digits."

class DigitsBetweenRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if len(params) < 2 or not isinstance(value, str):
            return False
            
        try:
            min_digits = int(params[0])
            max_digits = int(params[1])
        except ValueError:
            return False
            
        return value.isdigit() and min_digits <= len(value) <= max_digits
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be between {params[0]} and {params[1]} digits."

class MultipleOfRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        try:
            divisor = float(params[0])
            if divisor == 0:
                return False
            num = float(value)
            return num % divisor == 0
        except (ValueError, TypeError):
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The :name must be a multiple of {params[0]}."