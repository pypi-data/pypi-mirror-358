from .base import ValidationRule
from typing import Any, Dict, List, Optional, Set, Union, Tuple, Type

class FileRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        # 1. Cek file object framework (Flask/Werkzeug/FastAPI)
        if (hasattr(value, 'filename') and 
            hasattr(value, 'stream') and 
            hasattr(value, 'content_type')):
            return True
            
        # 2. Cek file-like object umum
        if hasattr(value, 'read') and callable(value.read):
            return True
            
        # 3. Cek path file yang valid (string)
        if isinstance(value, str):
            return (
                '.' in value and                  # Harus punya extension
                not value.startswith('data:') and # Bukan data URI
                not value.strip().startswith('<') # Bukan XML/HTML
            )
            
        # 4. Cek binary data langsung
        if isinstance(value, (bytes, bytearray)):
            return len(value) > 0  # Pastikan tidak kosong
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The {field} must be a valid file"

class DimensionsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        try:
            from PIL import Image
            import io

            # 1. Parse dimension rules
            min_width = min_height = 0
            max_width = max_height = float('inf')
            
            for param in params:
                try:
                    if param.startswith('min:'):
                        min_width, min_height = map(int, param[4:].split('x'))
                    elif param.startswith('max:'):
                        max_width, max_height = map(int, param[4:].split('x'))
                    else:
                        exact_width, exact_height = map(int, param.split('x'))
                        min_width = max_width = exact_width
                        min_height = max_height = exact_height
                except (ValueError, IndexError):
                    continue

            # 2. Load image with proper handling
            img = None
            try:
                # Case 1: File-like object (Flask/Werkzeug/FastAPI)
                if hasattr(value, 'read'):
                    value.seek(0)  # Important for rewinding
                    img = Image.open(value)
                    value.seek(0)  # Reset after reading
                
                # Case 2: Bytes data
                elif isinstance(value, bytes):
                    img = Image.open(io.BytesIO(value))
                
                # Case 3: File path (string)
                elif isinstance(value, str) and value.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    img = Image.open(value)
                
                if img is None:
                    return False

                # 3. Validate dimensions
                width, height = img.size
                return (min_width <= width <= max_width and 
                        min_height <= height <= max_height)

            except (IOError, OSError, AttributeError) as e:
                print(f"Image loading failed: {str(e)}")
                return False

        except Exception as e:
            print(f"Unexpected error in dimension validation: {str(e)}")
            return False
    
    def message(self, field: str, params: List[str]) -> str:
        min_rules = [p for p in params if p.startswith('min:')]
        max_rules = [p for p in params if p.startswith('max:')]
        exact_rules = [p for p in params if ':' not in p]
        
        messages = []
        if exact_rules:
            messages.append(f"exactly {exact_rules[0]}")
        if min_rules:
            messages.append(f"minimum {min_rules[0][4:]}")
        if max_rules:
            messages.append(f"maximum {max_rules[0][4:]}")
            
        return f"Image {field} dimensions must be {' and '.join(messages)}"
    
class ExtensionsRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        filename = (
            value.filename if hasattr(value, 'filename') 
            else str(value)
        ).lower()
        
        if '.' not in filename:
            return False
            
        ext = filename.rsplit('.', 1)[1]
        return ext in [e.lower().strip() for e in params]
    
    def message(self, field: str, params: List[str]) -> str:
        return f"File {field} must have one of these extensions: {', '.join(params)}"
    
class ImageRule(ValidationRule):
    VALID_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'}
    VALID_MIME_TYPES = {
        'image/jpeg', 'image/png', 
        'image/gif', 'image/bmp', 'image/webp'
    }

    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        # Check basic file attributes
        if not hasattr(value, 'filename') and not isinstance(value, (str, bytes)):
            return False
            
        # Check extension if available
        if hasattr(value, 'filename'):
            ext = value.filename.rsplit('.', 1)[-1].lower()
            if ext not in self.VALID_EXTENSIONS:
                return False
                
        # Check MIME type if available
        if hasattr(value, 'content_type'):
            if value.content_type not in self.VALID_MIME_TYPES:
                return False
                
        return True
    
    def message(self, field: str, params: List[str]) -> str:
        return f"The {field} must be a valid image file (JPEG, PNG, GIF, BMP, or WebP)"
    
class MimeTypesRule(ValidationRule):
    def validate(self, field: str, value: Any, params: List[str]) -> bool:
        if not params:
            return False
            
        # Check from content_type attribute
        if hasattr(value, 'content_type'):
            return value.content_type in params
            
        # Check from mimetype attribute
        if hasattr(value, 'mimetype'):
            return value.mimetype in params
            
        return False
    
    def message(self, field: str, params: List[str]) -> str:
        return f"File {field} must be one of these types: {', '.join(params)}"