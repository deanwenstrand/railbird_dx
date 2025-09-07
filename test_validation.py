#!/usr/bin/env python3
"""
PlayScript Validation Test Suite

Tests the validation tool with various valid and invalid PlayScript files.
"""

import os
import tempfile
import shutil
from pathlib import Path
from validate import PlayScriptValidator

def create_test_files():
    """Create test files for validation"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Valid action file
    (test_dir / "valid_action.ps").write_text("""
type: action
name: test.action
description: "A valid test action"
implementation: llm
enabled: true
effect: read
tags: [test, ai]

input_schema:
  message: {}
  
output_schema:
  response: {}

defaults:
  system_prompt: "You are a helpful assistant."
  user_prompt: "{{message}}"
""".strip())

    # Invalid action file (missing required fields)
    (test_dir / "invalid_action.ps").write_text("""
type: action
name: test.invalid
# Missing description and implementation
enabled: true

input_schema:
  message: {}
""".strip())

    # Valid schema file
    (test_dir / "valid_schema.ps").write_text("""
type: schema
object: test_object
view_name: Test Objects
description: "A test schema"

fields:
  - name: id
    view_name: ID
    type: string
    required: true
    primary_key: true
    
  - name: name
    view_name: Name
    type: string
    required: true
    length: 100
    
  - name: status
    view_name: Status
    type: picklist.excl
    required: false
    values:
      - active
      - inactive
    default: active
""".strip())

    # Valid layout file
    (test_dir / "valid_layout.ps").write_text("""
type: layout
name: test_object
description: "Layout for test object"

components:
  - type: field_section
    name: basic_info
    view_name: Basic Information
    location: main
    layout: two_column
    fields:
      - name
      - status
""".strip())

    # Valid automation file
    (test_dir / "valid_automation.ps").write_text("""
type: automation
name: test_automation
description: "Test automation"
enabled: true

trigger:
  type: database_event
  on: record_created
  tables: [test_object]

action:
  ref: test.action
  with:
    message: "New record created"
""".strip())

    # Invalid automation (missing action reference)
    (test_dir / "invalid_automation.ps").write_text("""
type: automation
name: invalid_automation
description: "Invalid automation"
enabled: true

trigger:
  type: database_event
  on: record_created
  tables: [test_object]

action:
  ref: nonexistent.action
  with:
    message: "This will fail"
""".strip())

    # YAML syntax error
    (test_dir / "yaml_error.ps").write_text("""
type: action
name: yaml_error
description: "File with YAML syntax error"
invalid_yaml: [unclosed list
""".strip())

    return test_dir

def run_tests():
    """Run validation tests"""
    print("🧪 PlayScript Validation Test Suite")
    print("=" * 50)
    
    test_dir = create_test_files()
    
    try:
        # Test 1: Validate all files (should find errors)
        print("\n📝 Test 1: Validate all test files")
        validator = PlayScriptValidator(str(test_dir))
        success = validator.validate_all()
        
        expected_errors = [
            "missing_required_field",  # invalid_action.ps
            "missing_action_reference",  # invalid_automation.ps  
            "yaml_syntax"  # yaml_error.ps
        ]
        
        found_error_types = [error.error_type for error in validator.errors]
        
        print(f"Expected errors: {len(expected_errors)}")
        print(f"Found errors: {len(validator.errors)}")
        
        for expected in expected_errors:
            if expected in found_error_types:
                print(f"  ✅ Found expected error: {expected}")
            else:
                print(f"  ❌ Missing expected error: {expected}")
        
        # Test 2: Syntax-only validation
        print("\n📝 Test 2: Syntax-only validation")
        validator2 = PlayScriptValidator(str(test_dir))
        validator2.validate_all(syntax_only=True)
        print(f"Syntax errors found: {len(validator2.errors)}")
        
        # Test 3: Cross-file only validation
        print("\n📝 Test 3: Cross-file validation only")
        validator3 = PlayScriptValidator(str(test_dir))
        validator3.validate_all(cross_file_only=True)
        print(f"Cross-file errors found: {len(validator3.errors)}")
        
        # Test 4: Validate specific file
        print("\n📝 Test 4: Validate specific file")
        validator4 = PlayScriptValidator(str(test_dir))
        validator4.validate_all(target_path="valid_action.ps")
        print(f"Errors in valid_action.ps: {len(validator4.errors)}")
        
        print("\n🎉 Test suite completed!")
        
    finally:
        # Clean up test files
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up test files")

if __name__ == "__main__":
    run_tests()
