import inspect
from .base import ValidationRule
from . import array, basic, comparison, date, type, files, format, conditional, string, utilities

def _collect_rules():
    modules = [array, basic, comparison, date, type, files, format, conditional, string, utilities]
    rules = {}
    
    for module in modules:
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, ValidationRule) and 
                obj != ValidationRule):
                rules[obj.rule_name] = obj
    return rules

all_rules = _collect_rules()

for name, cls in all_rules.items():
    globals()[cls.__name__.replace('Rule', '')] = cls  # Export class name
    globals()[name] = cls  # Export rule name


__all__ = ['ValidationRule'] + \
        list(all_rules.keys()) + \
        [cls.__name__.replace('Rule', '') for cls in all_rules.values()]