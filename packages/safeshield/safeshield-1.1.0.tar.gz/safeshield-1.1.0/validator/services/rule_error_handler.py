from typing import Dict, List, Any

class RuleErrorHandler:
    """Manages validation errors and message formatting"""
    def __init__(self, messages: Dict[str, str], custom_attributes: Dict[str, str]):
        self.messages = messages or {}
        self.custom_attributes = custom_attributes or {}
        self.errors: Dict[str, List[str]] = {}

    def add_error(self, field: str, rule_name: str, default_message: str, value: Any):
        """Add formatted error message"""
        message = self._format_message(field, rule_name, default_message, value)
        
        # Handle nested field display names
        self.errors.setdefault(field, []).append(message)

    def _format_message(self, field: str, rule_name: str, default_message: str, value: Any) -> str:
        """Format error message with placeholders"""
        # Get the base field name (last part of nested path)
        base_field = field.split('.')[-1]
        
        attribute = self.custom_attributes.get(field) or self.custom_attributes.get(base_field, field)
        value_str = str(value) if value is not None else ''
        
        message = (
            self.messages.get(field) or
            self.messages.get(attribute) or
            self.messages.get(f"{attribute}.*") or
            self.messages.get(f"{field}.{rule_name}") or
            default_message
        )
        
        return (message
            .replace(':name', attribute)
            .replace(':value', value_str)
            .replace(':param', rule_name.split(':')[1] if ':' in rule_name else '')
        )

    @property
    def has_errors(self) -> bool:
        """Check if any errors exist"""
        return bool(self.errors)