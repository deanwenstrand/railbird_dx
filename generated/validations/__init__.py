"""
Generated Validation Package
Auto-generated from PlayScript validation files - DO NOT EDIT
"""

# Empty validation system - no rules configured

class EmptyValidationEngine:
    """Empty validation engine when no rules are configured."""
    
    def validate_target(self, target: str, data: dict) -> dict:
        """Always returns valid for empty system."""
        return {
            'is_valid': True,
            'errors': [],
            'field_errors': {}
        }

# Empty instances
validation_engine = EmptyValidationEngine()
VALIDATION_RULES = {}

def get_validation_rules_for_target(target: str) -> list:
    return []

def get_all_targets() -> list:
    return []

def get_rule_count() -> int:
    return 0
