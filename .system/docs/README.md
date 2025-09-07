# PlayScript Language & Validation Tools

This directory contains everything you need to develop with the PlayScript language - a declarative YAML-based language for defining business applications, automations, and AI workflows.

## 📚 What's Included

- **[PLAYSCRIPT_LANGUAGE_GUIDE.md](PLAYSCRIPT_LANGUAGE_GUIDE.md)** - Complete language reference
- **[validate.py](validate.py)** - Standalone validation tool
- **[test_validation.py](test_validation.py)** - Test suite for the validator
- **Example PlayScript files** - Real working examples in subdirectories

## 🚀 Quick Start

### 1. Validate Your PlayScript Files

```bash
# Validate all files in current directory
python validate.py

# Validate specific file
python validate.py actions/email_draft.ps

# Validate specific directory
python validate.py actions/

# Only syntax validation (faster)
python validate.py --syntax-only

# Only cross-file reference validation
python validate.py --cross-file
```

### 2. Run Tests

```bash
# Test the validation tool
python test_validation.py
```

### 3. Learn the Language

Read the [PlayScript Language Guide](PLAYSCRIPT_LANGUAGE_GUIDE.md) for complete documentation.

## 📁 Directory Structure

```
playbook/
├── actions/           # Executable actions (LLM, API calls, orchestrations)
├── schemas/           # Database table definitions
├── layouts/           # UI layout definitions
├── automations/       # Event-driven workflows
├── integrations/      # External service connections
├── content/
│   ├── forms/         # Data collection forms
│   └── email_templates/  # Email templates
├── embeddings/        # Semantic search configurations
├── endpoints/         # Custom API endpoints
├── reports/           # Report definitions
├── validations/       # Validation rules
└── tests/             # Test definitions
```

## 🔧 Validation Features

The validation tool provides:

### Syntax Validation
- ✅ YAML syntax checking
- ✅ Required field validation
- ✅ Type-specific field validation
- ✅ Enum value validation
- ✅ Schema structure validation

### Cross-File Validation
- ✅ Action reference validation
- ✅ Schema field reference validation
- ✅ Object reference validation
- ✅ Integration reference validation
- ✅ Orchestration step validation

### Output Features
- 🎨 Colored terminal output
- 📊 Validation summary statistics
- ⚠️ Warnings for non-critical issues
- 🔍 Detailed error messages

## 📖 Language Overview

PlayScript supports several file types:

### Actions (`actions/`)
Executable units that can be called by AI or other actions:

```yaml
type: action
name: email.draft
description: "Draft a professional email"
implementation: llm
tags: [ai, email]

input_schema:
  to: {}
  subject: {}

output_schema:
  subject: {}
  body: {}

defaults:
  system_prompt: "You are a professional email writer..."
  user_prompt: "Draft email to {{to}} about {{subject}}"
```

### Schemas (`schemas/`)
Database table definitions:

```yaml
type: schema
object: contact
description: "Contact records"

fields:
  - name: id
    type: string
    primary_key: true
  - name: email
    type: email
    required: true
  - name: status
    type: picklist.excl
    values: [active, inactive]
```

### Layouts (`layouts/`)
UI layout definitions:

```yaml
type: layout
name: contact
description: "Contact detail page"

components:
  - type: field_section
    name: basic_info
    fields: [first_name, last_name, email]
```

### Automations (`automations/`)
Event-driven workflows:

```yaml
type: automation
name: welcome_email
description: "Send welcome email to new contacts"

trigger:
  type: database_event
  on: record_created
  tables: [contact]

action:
  ref: email.send_welcome
  with:
    contact_id: "{{trigger.record.id}}"
```

## 🎯 Use Cases

PlayScript is perfect for:

- **CRM Systems** - Define contacts, accounts, activities
- **AI Workflows** - Create LLM-powered actions and orchestrations
- **Business Automation** - Event-driven workflows and integrations
- **Form Processing** - Data collection and validation
- **API Development** - Auto-generated REST endpoints
- **Report Generation** - Data analysis and reporting

## 🔍 Example Validation Output

```
🔍 PlayScript Validation Tool
Validating: all files
--------------------------------------------------
📝 Validating syntax...
🔗 Validating cross-file references...

❌ 2 Error(s) Found:
  • invalid_action.ps: Missing required field: description
  • broken_automation.ps: Action not found: nonexistent.action

⚠️  1 Warning(s):
  • contact_layout.ps: Unknown field type: custom_type

📊 Summary:
  Files validated: 15
  Schemas found: 3
  Actions found: 8
  Integrations found: 2
```

## 🛠️ Development Workflow

1. **Write PlayScript files** using the language guide
2. **Validate frequently** with `python validate.py`
3. **Fix errors** based on validation output
4. **Test cross-file references** to ensure consistency
5. **Deploy** to your PlayScript runtime environment

## 🤝 Contributing

When adding new PlayScript files:

1. Follow naming conventions (snake_case)
2. Include meaningful descriptions
3. Use appropriate tags for AI discovery
4. Validate before committing
5. Test cross-file references

## 📋 Validation Checklist

Before deploying PlayScript files:

- [ ] All files pass syntax validation
- [ ] No cross-file reference errors
- [ ] Required fields are present
- [ ] Field types are valid
- [ ] Action references exist
- [ ] Schema objects are defined
- [ ] Integration names match
- [ ] Orchestration steps are valid

## 🔗 Related Tools

- **PlayScript Runtime** - Executes PlayScript files
- **AI Planner** - Selects and executes actions
- **Schema Generator** - Creates database tables
- **UI Generator** - Builds user interfaces
- **API Generator** - Creates REST endpoints

---

For complete language documentation, see [PLAYSCRIPT_LANGUAGE_GUIDE.md](PLAYSCRIPT_LANGUAGE_GUIDE.md)