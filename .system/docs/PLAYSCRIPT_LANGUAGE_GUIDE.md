# PlayScript Language Guide

**PlayScript** is a declarative YAML-based language for defining business applications, automations, and AI workflows. This guide covers everything you need to know to write, validate, and execute PlayScript files.

## Table of Contents

1. [Language Overview](#language-overview)
2. [File Types](#file-types)
3. [Core Syntax](#core-syntax)
4. [Actions](#actions)
5. [Schemas](#schemas)
6. [Layouts](#layouts)
7. [Automations](#automations)
8. [Integrations](#integrations)
9. [Forms](#forms)
10. [Reports](#reports)
11. [Validation](#validation)
12. [Cross-File References](#cross-file-references)
13. [Best Practices](#best-practices)
14. [Examples](#examples)

## Language Overview

PlayScript uses YAML syntax to define declarative configurations that are compiled into executable code. Each `.ps` file represents a specific component of your application.

### Key Principles

- **Declarative**: Describe what you want, not how to do it
- **Type-Safe**: Strong typing with validation
- **Cross-Referenced**: Files can reference each other
- **AI-Enabled**: Built-in support for LLM actions and orchestrations
- **Database-First**: Schema-driven development

## File Types

PlayScript supports several file types, each with a specific purpose:

| Type | Directory | Purpose | Example |
|------|-----------|---------|---------|
| `action` | `actions/` | Define executable actions (LLM, API calls, orchestrations) | `email_draft.ps` |
| `schema` | `schemas/` | Define database tables and data models | `contact.ps` |
| `layout` | `layouts/` | Define UI layouts for data objects | `contact_detail.ps` |
| `automation` | `automations/` | Define event-driven workflows | `send_welcome_email.ps` |
| `integration` | `integrations/` | Define external service connections | `gmail_smtp.ps` |
| `form` | `content/forms/` | Define data collection forms | `contact_form.ps` |
| `report` | `reports/` | Define tabular data reports with filtering and sorting | `contacts_report.ps` |
| `embedding` | `embeddings/` | Define semantic search configurations | `default.ps` |
| `endpoint` | `endpoints/` | Define custom API endpoints | `webhook.ps` |

## Core Syntax

All PlayScript files start with a `type` declaration and follow YAML syntax:

```yaml
type: action  # Required: file type
name: my_action  # Required: unique identifier
description: "What this component does"  # Required: human-readable description
enabled: true  # Optional: enable/disable (default: true)

# Type-specific configuration follows...
```

### Common Fields

- `type`: The file type (action, schema, layout, etc.)
- `name`: Unique identifier within the type
- `description`: Human-readable description
- `enabled`: Boolean to enable/disable the component
- `tags`: Array of tags for categorization and discovery

### Template Variables

PlayScript supports template variables using `{{variable_name}}` syntax:

```yaml
user_prompt: |
  Hello {{name}}, your email is {{email}}.
  Today is {{now}}.
```

Built-in variables:
- `{{now}}`: Current timestamp
- `{{user_id}}`: Current user ID
- `{{env.VAR_NAME}}`: Environment variables

## Actions

Actions are executable units that can be called by the AI planner or other actions.

### Basic Action Structure

```yaml
type: action
name: my.action
description: "Description of what this action does"
implementation: llm  # llm, create_record, integration_call, orchestration
enabled: true
effect: read  # read, write
tags: [ai, crm]  # Tags for AI planner discovery
embed: true  # Include in semantic search
when_to_use: "When user wants to do X"  # AI guidance

input_schema:
  field1: {}  # Required input field
  field2: {}  # Another input field

output_schema:
  result: {}  # Expected output field
  success: {}

defaults:
  # Implementation-specific defaults
```

### Implementation Types

#### 1. LLM Actions

Use Large Language Models for text processing:

```yaml
type: action
name: email.draft
implementation: llm
defaults:
  system_prompt: |
    You are a professional email writer.
    Output ONLY JSON: {"subject":"...","body":"..."}
  user_prompt: |
    Draft an email to {{recipient}} about {{topic}}.
    Context: {{context}}
```

#### 2. Database Actions

Create, read, update, or delete records:

```yaml
type: action
name: contact.create
implementation: create_record
defaults:
  table: contact
  data:
    status: "active"
    created_at: "{{now}}"
  mapping:
    first_name: "{{first_name}}"
    last_name: "{{last_name}}"
    email: "{{email}}"
```

#### 3. Integration Actions

Call external APIs:

```yaml
type: action
name: send.email
implementation: integration_call
defaults:
  integration: gmail_smtp
  method: send_email
  mapping:
    to: "{{recipient}}"
    subject: "{{subject}}"
    body: "{{message}}"
```

#### 4. Orchestration Actions

Chain multiple actions together:

```yaml
type: action
name: process.lead
implementation: orchestration
defaults:
  return_final_only: true  # Return only last step's output
  steps:
    - ref: lead.validate
      with:
        email: "{{email}}"
        phone: "{{phone}}"
    - ref: contact.create
      with:
        first_name: "{{first_name}}"
        last_name: "{{last_name}}"
        email: "{{email}}"
        validation_result: "{{lead.validate.status}}"
    - ref: welcome.email
      with:
        contact_id: "{{contact.create.id}}"
```

### AI-Specific Fields

For actions that should be available to the AI planner:

```yaml
tags: [ai]  # Must include 'ai' tag
namespace: ai  # Optional: group related actions
ui_component: email_draft  # Optional: UI component to render
when_to_use: "When user wants to draft an email"  # AI guidance
```

## Schemas

Schemas define database tables and data models.

### Basic Schema Structure

```yaml
type: schema
object: contact  # Table name
view_name: Contacts  # Human-readable name
description: "Contact records for people at customer accounts"
deletion_mode: soft  # soft, hard

endpoints:  # Auto-generate REST endpoints
  - GET
  - POST
  - PUT /{id}
  - DELETE /{id}

add_to_top_nav: true  # Show in navigation
search:
  enabled: true
  label: "Contacts"

fields:
  - name: id
    view_name: ID
    type: string
    required: true
    primary_key: true
    system_managed: true

  - name: email
    view_name: Email Address
    type: email
    required: true
    length: 150

  - name: status
    view_name: Status
    type: picklist.excl
    required: false
    values:
      - active
      - inactive
    default: active
```

### Field Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text field | `"John Doe"` |
| `email` | Email validation | `"user@example.com"` |
| `datetime` | Timestamp | `"2025-01-16T10:30:00Z"` |
| `integer` | Whole number | `42` |
| `decimal` | Decimal number | `99.99` |
| `boolean` | True/false | `true` |
| `textarea` | Long text | Multi-line text |
| `picklist.excl` | Single choice | One value from list |
| `picklist.multi` | Multiple choice | Multiple values from list |

### Relationships

Define relationships between objects:

```yaml
fields:
  - name: account_id
    type: string
    foreign_key:
      table: account
      column: id
      kind: lookup  # lookup, master_detail
      on_delete: nullify  # nullify, cascade, restrict

joins:
  - name: activities
    view_name: Activities
    object: activity
    type: one_to_many
    condition: contact.id matches activity.contact_id
    sort:
      field: created_at
      direction: desc
    limit: 10
```

## Layouts

Layouts define how data objects are displayed in the UI.

### Basic Layout Structure

```yaml
type: layout
name: contact
add_to_global_nav: true
weight: 150  # Navigation order
description: "Contact detail page layout"

components:
  - type: field_section
    name: basic_info
    view_name: Contact Information
    location: main  # main, sidebar, footer, top_navigation
    layout: two_column  # single_column, two_column, flex-wrap
    fields:
      - first_name           # Auto-flows to columns
      - last_name
      - name: email
        column: 1            # Force to left column
        style_override:
          color: "#0070d2"
          font_weight: bold
      - name: phone
        column: 2            # Force to right column
      - title                # Auto-flows

  - type: related_list
    name: activities
    view_name: Recent Activities
    location: top_navigation
    data: activity
    limit: 10
    fields:
      - type
      - direction
      - status
      - created_at
```

### Component Types

- `field_section`: Display object fields
- `related_list`: Display related records
- `custom_component`: Custom React component

### Field Section Layouts

Field sections support different layout types:

- **`single_column`**: All fields stack vertically
- **`two_column`**: Fields flow left-to-right, wrapping to next row
- **`flex-wrap`**: Fields flow horizontally and wrap (ideal for action buttons)

### Column Placement (two_column only)

Control exactly which fields go in which column:

```yaml
layout: two_column
fields:
  - name: first_name
    column: 1              # Left column
  - name: last_name
    column: 2              # Right column
  - phone                  # Auto-flows (left column)
  - email                  # Auto-flows (right column)
  - name: send_email
    type: action
    column: 2              # Action button in right column
```

**How it works:**
1. Fields with `column: 1` render first in left column
2. Fields with `column: 2` render first in right column  
3. Fields without `column` auto-flow left-right-left-right
4. Works with any field type: regular fields, lookups, actions

## Automations

Automations define event-driven workflows.

### Basic Automation Structure

```yaml
type: automation
name: welcome_new_contact
description: "Send welcome email when new contact is created"
enabled: true

trigger:
  type: database_event
  on: record_created  # record_created, record_updated, record_deleted
  tables: [contact]
  
  # Optional filters
  filters:
    status: "active"
    email: "!null"  # Not null

action:
  ref: send.welcome_email  # Reference to action
  with:
    contact_id: "{{trigger.record.id}}"
    email: "{{trigger.record.email}}"
    name: "{{trigger.record.first_name}}"
```

### Trigger Types

- `database_event`: Database record changes
- `schedule`: Time-based triggers
- `webhook`: HTTP webhook triggers
- `manual`: User-initiated triggers

## Integrations

Integrations define connections to external services.

### Basic Integration Structure

```yaml
type: integration
name: gmail_smtp
service: email
description: "Send emails via Gmail SMTP"

connection:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  use_tls: true

auth:
  type: basic_auth
  username_env: GMAIL_USERNAME
  password_env: GMAIL_APP_PASSWORD

request_mapping:
  to: "{{recipient_email}}"
  subject: "{{subject}}"
  body: "{{message}}"
  from_name: "My App"
  from_email: "{{env.GMAIL_USERNAME}}"

response_mapping:
  success_condition: "smtp_response == 'success'"

error_handling:
  on_failure: log_error
  retry_attempts: 3
```

## Forms

Forms define data collection interfaces.

### Basic Form Structure

```yaml
type: form
name: contact_capture_form
title: Contact Capture Form
description: "Collect contact information"

target_object: contact
action: upsert  # create, update, upsert
match_conditions:
  - field: email
    value: "{form.email}"
    operator: iequals
on_no_match: create_new
on_multiple_matches: update_first

success_message: "Thank you! Your contact has been submitted."
error_message: "Error processing your submission. Please try again."

fields:
  - maps_to: contact.first_name
    placeholder: "Enter your first name"
    behavior: overwrite  # overwrite, append, preserve

  - maps_to: contact.email
    placeholder: "user@company.com"
    behavior: overwrite

embed:
  domains: ["*.yourdomain.com", "localhost"]
  style: "minimal"
  theme: "default"
```

## Reports

Reports define tabular data displays with filtering, sorting, and pagination.

### Basic Report Structure

```yaml
type: report
name: contacts_report
title: Contact List Report
description: Simple tabular report showing contact information
source: Contact  # Source model name

fields:
  - first_name
  - last_name
  - email
  - phone
  - status
  - created_date

options:
  pagination: true
  page_size: 50
  sortable: true
  filterable: true

filters:
  - field: status
    type: string
    operator: equals
    label: Status
    
  - field: last_name
    type: string
    operator: contains
    label: Last Name
```

### Report Fields

- `source`: The model/table to query data from
- `fields`: Array of field names to display as columns
- `options`: Display and interaction options
- `filters`: Available filters for users

### Filter Types

| Type | Operators | Description |
|------|-----------|-------------|
| `string` | `equals`, `contains`, `like` | Text filtering |
| `number` | `equals`, `gt`, `lt`, `gte`, `lte` | Numeric filtering |
| `date` | `equals`, `before`, `after` | Date filtering |
| `enum` | `equals` | Choice from predefined values |

## Validation

PlayScript includes comprehensive validation for syntax and cross-file references.

### Syntax Validation

Each file type has specific validation rules:

- **Required fields**: `type`, `name`, `description`
- **Type-specific fields**: Based on the `type` value
- **Data types**: String, boolean, array, object validation
- **Enum values**: Restricted choice validation

### Cross-File Validation

Validates references between files:

- **Action references**: Automations referencing actions
- **Schema references**: Layouts referencing schema fields
- **Object references**: Forms targeting schema objects
- **Join references**: Schema joins referencing other objects

## Cross-File References

PlayScript files can reference each other using dot notation:

### Action References

```yaml
# In automation file
action:
  ref: contact.create  # References actions/contact_create.ps
```

### Schema Field References

```yaml
# In layout file
fields:
  - first_name  # References schema field
  - contact.email  # Explicit object.field reference
```

### Object References

```yaml
# In form file
target_object: contact  # References schemas/contact.ps
```

## Best Practices

### 1. Naming Conventions

- Use snake_case for file names: `contact_create.ps`
- Use dot notation for action names: `contact.create`
- Use descriptive names: `send_welcome_email` not `email1`

### 2. Organization

- Group related actions in subdirectories
- Use consistent naming patterns
- Keep files focused on single responsibility

### 3. Documentation

- Always include meaningful descriptions
- Use `when_to_use` for AI-enabled actions
- Comment complex logic in prompts

### 4. Error Handling

- Include error handling in integrations
- Validate inputs in LLM prompts
- Use appropriate `effect` values (read/write)

### 5. Performance

- Use `embed: true` for searchable actions
- Limit related list results
- Use appropriate field types

## Examples

### Complete Email Workflow

**Action: Draft Email**
```yaml
# actions/email_draft.ps
type: action
name: email.draft
description: "Draft a professional email"
implementation: llm
enabled: true
effect: read
tags: [ai, email]
ui_component: email_draft

input_schema:
  to: {}
  subject_hint: {}
  context: {}

output_schema:
  subject: {}
  body: {}
  to: {}

defaults:
  system_prompt: |
    You are a professional email writer.
    Output ONLY JSON: {"subject":"...","body":"...","to":"..."}
    Keep subject under 8 words.
    Keep body concise and professional.
  user_prompt: |
    Draft email to: {{to}}
    Subject hint: {{subject_hint}}
    Context: {{context}}
```

**Action: Send Email**
```yaml
# actions/email_send.ps
type: action
name: email.send
description: "Send email via integration"
implementation: integration_call
enabled: true
effect: write
tags: [email]

input_schema:
  to: {}
  subject: {}
  body: {}

output_schema:
  success: {}
  message_id: {}

defaults:
  integration: gmail_smtp
  method: send_email
  mapping:
    to: "{{to}}"
    subject: "{{subject}}"
    body: "{{body}}"
```

**Orchestration: Complete Email Flow**
```yaml
# actions/email_workflow.ps
type: action
name: email.workflow
description: "Draft and send email workflow"
implementation: orchestration
enabled: true
effect: write
tags: [ai, email, workflow]

input_schema:
  recipient: {}
  topic: {}
  context: {}

output_schema:
  success: {}
  message_id: {}

defaults:
  return_final_only: true
  steps:
    - ref: email.draft
      with:
        to: "{{recipient}}"
        subject_hint: "{{topic}}"
        context: "{{context}}"
    - ref: email.send
      with:
        to: "{{email.draft.to}}"
        subject: "{{email.draft.subject}}"
        body: "{{email.draft.body}}"
```

### Complete CRM Schema

```yaml
# schemas/contact.ps
type: schema
object: contact
view_name: Contacts
description: "Contact records for people at customer accounts"
deletion_mode: soft

endpoints:
  - GET
  - POST
  - GET /{id}
  - PUT /{id}
  - DELETE /{id}

add_to_top_nav: true
search:
  enabled: true
  label: "Contacts"

fields:
  - name: id
    view_name: ID
    type: string
    required: true
    primary_key: true
    system_managed: true

  - name: first_name
    view_name: First Name
    type: string
    required: false
    length: 50

  - name: last_name
    view_name: Last Name
    type: string
    required: false
    length: 50

  - name: email
    view_name: Email Address
    type: email
    required: true
    length: 150

  - name: phone
    view_name: Phone Number
    type: string
    required: false
    length: 50

  - name: status
    view_name: Status
    type: picklist.excl
    required: false
    values:
      - active
      - inactive
    default: active

  - name: account_id
    view_name: Account
    type: string
    required: false
    foreign_key:
      table: account
      column: id
      kind: lookup
      on_delete: nullify

  # System fields
  - name: created_at
    view_name: Created At
    type: datetime
    required: false
    system_managed: true

  - name: updated_at
    view_name: Updated At
    type: datetime
    required: false
    system_managed: true

joins:
  - name: activities
    view_name: Activities
    object: activity
    type: one_to_many
    condition: contact.id matches activity.contact_id
    sort:
      field: created_at
      direction: desc
    limit: 10
```

This guide covers the complete PlayScript language. Use the validation tools in this directory to ensure your PlayScript files are correct and properly cross-referenced.
