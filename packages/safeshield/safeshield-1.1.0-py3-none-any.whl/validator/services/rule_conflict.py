from typing import List, Set, Dict, Tuple
import warnings

class RuleConflictChecker:
    """Class untuk mendeteksi dan menangani konflik antar validation rules."""
    
    # Daftar konflik kritis yang akan memunculkan exception
    CRITICAL_CONFLICTS = [
        # Mutually exclusive presence
        ('required', 'nullable'),
        ('required', 'sometimes'),
        ('filled', 'prohibited_if'),
        
        # Type conflicts
        ('numeric', 'email'),
        ('numeric', 'array'),
        ('boolean', 'integer'),
        ('boolean', 'numeric'),
        ('array', 'string'),
        
        # Format conflicts
        ('email', 'ip'),
        ('uuid', 'ulid'),
        ('json', 'timezone'),
        
        # Value requirement conflicts
        ('accepted', 'declined'),
        ('same', 'different')
    ]
    
    # Daftar konflik fungsional yang hanya memunculkan warning
    WARNING_CONFLICTS = [
        # Overlapping validation
        ('between', 'digits_between'),
        ('min', 'size'),
        ('max', 'size'),
        ('confirmed', 'same'),
        ('in', 'not_in'),
        
        # Redundant type checks
        ('integer', 'numeric'),
        ('alpha_num', 'alpha_dash'),
        ('starts_with', 'ends_with'),
        
        # Similar format checks
        ('url', 'json'),
        ('ulid', 'uuid')
    ]
    
    # Grup rules yang saling terkait
    REQUIRED_GROUPS = {
        'required_with', 'required_with_all',
        'required_without', 'required_without_all'
    }
    
    PROHIBITED_GROUPS = {
        'prohibited_if', 'prohibited_unless'
    }

    @classmethod
    def check_conflicts(cls, rules: List['ValidationRule']) -> None:
        """Main method untuk mengecek semua jenis konflik.
        
        Args:
            rules: List of ValidationRule objects to check
            
        Raises:
            ValueError: Untuk konflik kritis
            UserWarning: Untuk konflik fungsional/potensial
        """
        rule_names = {r.rule_name for r in rules}
        params_map = {r.rule_name: r.params for r in rules}
        
        cls._check_critical_conflicts(rule_names)
        cls._check_warning_conflicts(rule_names)
        cls._check_parameter_conflicts(rule_names, params_map)
        cls._check_special_cases(rule_names)

    @classmethod
    def _check_critical_conflicts(cls, rule_names: Set[str]) -> None:
        """Cek konflik kritis yang akan memunculkan exception."""
        for rule1, rule2 in cls.CRITICAL_CONFLICTS:
            if rule1 in rule_names and rule2 in rule_names:
                raise ValueError(
                    f"Critical rule conflict: '{rule1}' cannot be used with '{rule2}'"
                )

    @classmethod
    def _check_warning_conflicts(cls, rule_names: Set[str]) -> None:
        """Cek konflik fungsional yang hanya memunculkan warning."""
        for rule1, rule2 in cls.WARNING_CONFLICTS:
            if rule1 in rule_names and rule2 in rule_names:
                warnings.warn(f"Potential overlap: '{rule1}' and '{rule2}' may validate similar things", UserWarning, stacklevel=2)

    @classmethod
    def _check_parameter_conflicts(cls, rule_names: Set[str], params_map: Dict[str, List[str]]) -> None:
        """Cek konflik parameter antar rules."""
        # Range conflicts
        if 'min' in rule_names and 'max' in rule_names:
            min_val = float(params_map['min'][0])
            max_val = float(params_map['max'][0])
            if min_val > max_val:
                raise ValueError(f"Invalid range: min ({min_val}) > max ({max_val})")

        if 'between' in rule_names:
            between_vals = params_map['between']
            
            if len(between_vals) != 2:
                raise ValueError("Between rule requires exactly 2 values")
            min_val, max_val = map(float, between_vals)
            if min_val >= max_val:
                raise ValueError(f"Invalid between range: {min_val} >= {max_val}")

        # Size vs length checks
        if 'size' in rule_names and ('min' in rule_names or 'max' in rule_names):
            warnings.warn("'size' already implies exact dimension, 'min/max' may be redundant", UserWarning)

    @classmethod
    def _check_special_cases(cls, rule_names: Set[str]) -> None:
        """Cek special cases dan grup rules."""
        # Required_with/without group conflicts
        if len(cls.REQUIRED_GROUPS & rule_names) > 1:
            warnings.warn(
                "Multiple required_* conditions may cause unexpected behavior",
                UserWarning
            )

        # Prohibited_if/unless conflicts
        if len(cls.PROHIBITED_GROUPS & rule_names) > 1:
            warnings.warn(
                "Using both prohibited_if and prohibited_unless may be confusing",
                UserWarning
            )