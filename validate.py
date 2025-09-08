#!/usr/bin/env python3
"""
PlayScript Validation Tool

Standalone validation tool for PlayScript files.
Validates both individual file syntax and cross-file references.

Usage:
    python validate.py                    # Validate all files
    python validate.py actions/          # Validate specific directory
    python validate.py contact.ps        # Validate specific file
    python validate.py --cross-file      # Only cross-file validation
    python validate.py --syntax-only     # Only syntax validation
"""

import os
import sys
import yaml
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class ValidationError:
    """Represents a validation error"""
    file_path: str
    error_type: str
    message: str
    line_number: Optional[int] = None
    severity: str = "error"  # error, warning, info

class PlayScriptValidator:
    """Main validator for PlayScript files"""
    
    def __init__(self, playbook_dir: str = "."):
        self.playbook_dir = Path(playbook_dir)
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        
        # Cross-file reference tracking
        self.schema_objects: Set[str] = set()
        self.schema_fields: Dict[str, Set[str]] = {}
        self.action_names: Set[str] = set()
        self.integration_names: Set[str] = set()
        self.all_files: Dict[str, Dict[str, Any]] = {}
        
    def validate_all(self, target_path: Optional[str] = None, syntax_only: bool = False, cross_file_only: bool = False) -> bool:
        """Validate all PlayScript files or specific target"""
        print(f"{Colors.BOLD}🔍 PlayScript Validation Tool{Colors.END}")
        print(f"Validating: {target_path or 'all files'}")
        print("-" * 50)
        
        if not cross_file_only:
            self._validate_syntax(target_path)
        
        if not syntax_only:
            self._validate_cross_file_references()
        
        self._print_results()
        return len(self.errors) == 0
    
    def _validate_syntax(self, target_path: Optional[str] = None):
        """Validate syntax of PlayScript files"""
        print(f"{Colors.CYAN}📝 Validating syntax...{Colors.END}")
        
        if target_path:
            target = self.playbook_dir / target_path
            if target.is_file() and target.suffix == '.ps':
                self._validate_file(target)
            elif target.is_dir():
                for ps_file in target.rglob("*.ps"):
                    self._validate_file(ps_file)
            else:
                self.errors.append(ValidationError(
                    str(target), "file_not_found", f"Target not found: {target_path}"
                ))
        else:
            # Validate all .ps files
            for ps_file in self.playbook_dir.rglob("*.ps"):
                self._validate_file(ps_file)
    
    def _validate_file(self, file_path: Path):
        """Validate a single PlayScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse YAML
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError as e:
                self.errors.append(ValidationError(
                    str(file_path), "yaml_syntax", f"YAML syntax error: {e}"
                ))
                return
            
            if not isinstance(data, dict):
                self.errors.append(ValidationError(
                    str(file_path), "invalid_format", "File must contain a YAML object"
                ))
                return
            
            # Store for cross-file validation
            self.all_files[str(file_path)] = data
            
            # Validate based on type
            file_type = data.get('type')
            if not file_type:
                self.errors.append(ValidationError(
                    str(file_path), "missing_type", "Missing required 'type' field"
                ))
                return
            
            # Type-specific validation
            if file_type == 'action':
                self._validate_action(file_path, data)
            elif file_type == 'schema':
                self._validate_schema(file_path, data)
            elif file_type == 'layout':
                self._validate_layout(file_path, data)
            elif file_type == 'automation':
                self._validate_automation(file_path, data)
            elif file_type == 'integration':
                self._validate_integration(file_path, data)
            elif file_type == 'form':
                self._validate_form(file_path, data)
            else:
                self.warnings.append(ValidationError(
                    str(file_path), "unknown_type", f"Unknown type: {file_type}", severity="warning"
                ))
                
        except Exception as e:
            self.errors.append(ValidationError(
                str(file_path), "file_error", f"Error reading file: {e}"
            ))
    
    def _validate_action(self, file_path: Path, data: Dict[str, Any]):
        """Validate action file"""
        required_fields = ['name', 'description', 'implementation']
        self._check_required_fields(file_path, data, required_fields)
        
        name = data.get('name')
        if name:
            self.action_names.add(name)
        
        implementation = data.get('implementation')
        valid_implementations = ['create_record', 'integration_call', 'python', 'api_call']
        if implementation and implementation not in valid_implementations:
            self.errors.append(ValidationError(
                str(file_path), "invalid_implementation", 
                f"Invalid implementation: {implementation}. Must be one of: {', '.join(valid_implementations)}"
            ))
        
        # Validate schemas
        if 'input_schema' in data and not isinstance(data['input_schema'], dict):
            self.errors.append(ValidationError(
                str(file_path), "invalid_schema", "input_schema must be an object"
            ))
        
        if 'output_schema' in data and not isinstance(data['output_schema'], dict):
            self.errors.append(ValidationError(
                str(file_path), "invalid_schema", "output_schema must be an object"
            ))
        
        # NOTE: orchestration validation removed - implementation type no longer supported
        
        # Validate tags
        tags = data.get('tags', [])
        if tags and not isinstance(tags, list):
            self.errors.append(ValidationError(
                str(file_path), "invalid_tags", "tags must be a list"
            ))
    
    def _validate_schema(self, file_path: Path, data: Dict[str, Any]):
        """Validate schema file"""
        required_fields = ['object', 'description', 'fields']
        self._check_required_fields(file_path, data, required_fields)
        
        object_name = data.get('object')
        if object_name:
            self.schema_objects.add(object_name)
            self.schema_fields[object_name] = set()
        
        fields = data.get('fields', [])
        if not isinstance(fields, list):
            self.errors.append(ValidationError(
                str(file_path), "invalid_fields", "fields must be a list"
            ))
            return
        
        field_names = set()
        for i, field in enumerate(fields):
            if not isinstance(field, dict):
                self.errors.append(ValidationError(
                    str(file_path), "invalid_field", f"Field {i} must be an object"
                ))
                continue
            
            field_name = field.get('name')
            if not field_name:
                self.errors.append(ValidationError(
                    str(file_path), "missing_field_name", f"Field {i} missing 'name'"
                ))
                continue
            
            if field_name in field_names:
                self.errors.append(ValidationError(
                    str(file_path), "duplicate_field", f"Duplicate field name: {field_name}"
                ))
            
            field_names.add(field_name)
            if object_name:
                self.schema_fields[object_name].add(field_name)
            
            # Validate field type
            field_type = field.get('type')
            valid_types = [
                'string', 'email', 'datetime', 'integer', 'decimal', 'boolean',
                'textarea', 'picklist.excl', 'picklist.multi'
            ]
            if field_type and field_type not in valid_types:
                self.warnings.append(ValidationError(
                    str(file_path), "unknown_field_type", 
                    f"Unknown field type: {field_type}", severity="warning"
                ))
            
            # Validate picklist values
            if field_type and field_type.startswith('picklist') and 'values' not in field:
                self.errors.append(ValidationError(
                    str(file_path), "missing_picklist_values", 
                    f"Picklist field {field_name} missing 'values'"
                ))
    
    def _validate_layout(self, file_path: Path, data: Dict[str, Any]):
        """Validate layout file"""
        required_fields = ['name', 'components']
        self._check_required_fields(file_path, data, required_fields)
        
        components = data.get('components', [])
        if not isinstance(components, list):
            self.errors.append(ValidationError(
                str(file_path), "invalid_components", "components must be a list"
            ))
            return
        
        for i, component in enumerate(components):
            if not isinstance(component, dict):
                self.errors.append(ValidationError(
                    str(file_path), "invalid_component", f"Component {i} must be an object"
                ))
                continue
            
            comp_type = component.get('type')
            valid_types = ['field_section', 'related_list', 'custom_component']
            if comp_type and comp_type not in valid_types:
                self.errors.append(ValidationError(
                    str(file_path), "invalid_component_type", 
                    f"Invalid component type: {comp_type}"
                ))
    
    def _validate_automation(self, file_path: Path, data: Dict[str, Any]):
        """Validate automation file"""
        required_fields = ['name', 'description', 'trigger', 'action']
        self._check_required_fields(file_path, data, required_fields)
        
        trigger = data.get('trigger', {})
        if isinstance(trigger, dict):
            trigger_type = trigger.get('type')
            valid_trigger_types = ['database_event', 'schedule', 'webhook', 'manual']
            if trigger_type and trigger_type not in valid_trigger_types:
                self.errors.append(ValidationError(
                    str(file_path), "invalid_trigger_type", 
                    f"Invalid trigger type: {trigger_type}"
                ))
        
        action = data.get('action', {})
        if isinstance(action, dict) and 'ref' not in action:
            self.errors.append(ValidationError(
                str(file_path), "missing_action_ref", "Action must have 'ref' field"
            ))
    
    def _validate_integration(self, file_path: Path, data: Dict[str, Any]):
        """Validate integration file"""
        required_fields = ['name', 'service', 'description']
        self._check_required_fields(file_path, data, required_fields)
        
        name = data.get('name')
        if name:
            self.integration_names.add(name)
    
    def _validate_form(self, file_path: Path, data: Dict[str, Any]):
        """Validate form file"""
        required_fields = ['name', 'title', 'target_object', 'fields']
        self._check_required_fields(file_path, data, required_fields)
        
        fields = data.get('fields', [])
        if not isinstance(fields, list):
            self.errors.append(ValidationError(
                str(file_path), "invalid_fields", "fields must be a list"
            ))
    
    def _check_required_fields(self, file_path: Path, data: Dict[str, Any], required_fields: List[str]):
        """Check for required fields"""
        for field in required_fields:
            if field not in data:
                self.errors.append(ValidationError(
                    str(file_path), "missing_required_field", f"Missing required field: {field}"
                ))
    
    def _validate_cross_file_references(self):
        """Validate cross-file references"""
        print(f"{Colors.CYAN}🔗 Validating cross-file references...{Colors.END}")
        
        for file_path, data in self.all_files.items():
            file_type = data.get('type')
            
            if file_type == 'automation':
                self._validate_automation_references(file_path, data)
            elif file_type == 'layout':
                self._validate_layout_references(file_path, data)
            elif file_type == 'form':
                self._validate_form_references(file_path, data)
            # NOTE: orchestration reference validation removed - implementation type no longer supported
            elif file_type == 'action' and data.get('implementation') == 'integration_call':
                self._validate_integration_references(file_path, data)
    
    def _validate_automation_references(self, file_path: str, data: Dict[str, Any]):
        """Validate automation action references"""
        action = data.get('action', {})
        if isinstance(action, dict):
            ref = action.get('ref')
            if ref and ref not in self.action_names:
                self.errors.append(ValidationError(
                    file_path, "missing_action_reference", f"Action not found: {ref}"
                ))
    
    def _validate_layout_references(self, file_path: str, data: Dict[str, Any]):
        """Validate layout schema references"""
        layout_name = data.get('name')
        if layout_name and layout_name not in self.schema_objects:
            self.warnings.append(ValidationError(
                file_path, "missing_schema_reference", 
                f"Schema not found for layout: {layout_name}", severity="warning"
            ))
        
        # Validate field references in components
        components = data.get('components', [])
        for component in components:
            if isinstance(component, dict):
                fields = component.get('fields', [])
                for field in fields:
                    if isinstance(field, str):
                        self._validate_field_reference(file_path, layout_name, field)
                    elif isinstance(field, dict) and 'name' in field:
                        self._validate_field_reference(file_path, layout_name, field['name'])
    
    def _validate_field_reference(self, file_path: str, object_name: str, field_name: str):
        """Validate a field reference"""
        if '.' in field_name:
            obj, field = field_name.split('.', 1)
            if obj in self.schema_fields and field not in self.schema_fields[obj]:
                self.errors.append(ValidationError(
                    file_path, "missing_field_reference", 
                    f"Field not found: {obj}.{field}"
                ))
        elif object_name in self.schema_fields and field_name not in self.schema_fields[object_name]:
            self.errors.append(ValidationError(
                file_path, "missing_field_reference", 
                f"Field not found: {object_name}.{field_name}"
            ))
    
    def _validate_form_references(self, file_path: str, data: Dict[str, Any]):
        """Validate form target object references"""
        target_object = data.get('target_object')
        if target_object and target_object not in self.schema_objects:
            self.errors.append(ValidationError(
                file_path, "missing_schema_reference", f"Target object not found: {target_object}"
            ))
        
        # Validate field mappings
        fields = data.get('fields', [])
        for field in fields:
            if isinstance(field, dict) and 'maps_to' in field:
                maps_to = field['maps_to']
                if '.' in maps_to:
                    obj, field_name = maps_to.split('.', 1)
                    if obj in self.schema_fields and field_name not in self.schema_fields[obj]:
                        self.errors.append(ValidationError(
                            file_path, "missing_field_reference", f"Field not found: {maps_to}"
                        ))
    
    # NOTE: _validate_orchestration_references method removed - implementation type no longer supported
    
    def _validate_integration_references(self, file_path: str, data: Dict[str, Any]):
        """Validate integration references"""
        defaults = data.get('defaults', {})
        integration = defaults.get('integration')
        if integration and integration not in self.integration_names:
            self.errors.append(ValidationError(
                file_path, "missing_integration_reference", f"Integration not found: {integration}"
            ))
    
    def _print_results(self):
        """Print validation results"""
        print()
        
        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}❌ {len(self.errors)} Error(s) Found:{Colors.END}")
            for error in self.errors:
                print(f"  {Colors.RED}•{Colors.END} {Path(error.file_path).name}: {error.message}")
        
        if self.warnings:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {len(self.warnings)} Warning(s):{Colors.END}")
            for warning in self.warnings:
                print(f"  {Colors.YELLOW}•{Colors.END} {Path(warning.file_path).name}: {warning.message}")
        
        if not self.errors and not self.warnings:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ All files are valid!{Colors.END}")
        elif not self.errors:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ No errors found (warnings only){Colors.END}")
        
        print()
        print(f"📊 Summary:")
        print(f"  Files validated: {len(self.all_files)}")
        print(f"  Schemas found: {len(self.schema_objects)}")
        print(f"  Actions found: {len(self.action_names)}")
        print(f"  Integrations found: {len(self.integration_names)}")

def main():
    parser = argparse.ArgumentParser(description="Validate PlayScript files")
    parser.add_argument("target", nargs="?", help="Specific file or directory to validate")
    parser.add_argument("--syntax-only", action="store_true", help="Only validate syntax")
    parser.add_argument("--cross-file", action="store_true", help="Only validate cross-file references")
    parser.add_argument("--playbook-dir", default=".", help="PlayScript directory (default: current)")
    
    args = parser.parse_args()
    
    validator = PlayScriptValidator(args.playbook_dir)
    success = validator.validate_all(
        target_path=args.target,
        syntax_only=args.syntax_only,
        cross_file_only=args.cross_file
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
