# factory.py
from typing import Type, Dict, List
from validator.rules import all_rules
from validator.rules.base import ValidationRule

class RuleFactory:
    _rules: Dict[str, Type[ValidationRule]] = all_rules
    
    @classmethod
    def create_rule(cls, rule_name: str) -> ValidationRule:
        try:
            return cls._rules[rule_name]()
        except KeyError:
            raise ValueError(f"Unknown validation rule: {rule_name}")
    
    @classmethod
    def register_rule(cls, name: str, rule_class: Type[ValidationRule]):
        cls._rules[name] = rule_class
        
    @classmethod
    def has_rule(cls, rule_name: str) -> bool:
        return rule_name in cls._rules

    @classmethod
    def get_rule_names(cls) -> List[str]:
        return list(cls._rules.keys())