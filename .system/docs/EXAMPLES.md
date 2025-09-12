# PlayScript Examples

This file contains practical examples of PlayScript files for common use cases.

## Email Workflow Example

### 1. Email Draft Action
**File: `actions/email_draft.ps`**

```yaml
type: action
name: email.draft
description: "Draft a professional email using AI"
implementation: llm
enabled: true
effect: read
tags: [ai, email, draft]
embed: true
when_to_use: "When user wants to draft an email"
ui_component: email_draft

input_schema:
  to: {}          # Recipient email
  subject: {}     # Email subject
  context: {}     # Additional context

output_schema:
  subject: {}     # Generated subject
  body: {}        # Generated email body
  to: {}          # Recipient email

defaults:
  system_prompt: |
    You are a professional email writer.
    Write clear, concise, and professional emails.
    Output ONLY JSON: {"subject":"...","body":"...","to":"..."}
    
    Rules:
    - Subject: Maximum 8 words
    - Body: 2-4 short sentences
    - Tone: Professional but friendly
    - No signatures or footers
    
  user_prompt: |
    Draft an email to: {{to}}
    Subject: {{subject}}
    Context: {{context}}
    
    Create a professional email based on this information.
```

### 2. Email Send Action
**File: `actions/email_send.ps`**

```yaml
type: action
name: email.send
description: "Send email via SMTP integration"
implementation: integration_call
enabled: true
effect: write
tags: [email, send]

input_schema:
  to: {}          # Recipient email
  subject: {}     # Email subject
  body: {}        # Email body
  from_name: {}   # Sender name (optional)

output_schema:
  success: {}     # Boolean success
  message_id: {}  # Email message ID
  error: {}       # Error message if failed

defaults:
  integration: gmail_smtp
  method: send_email
  mapping:
    to: "{{to}}"
    subject: "{{subject}}"
    body: "{{body}}"
    from_name: "{{from_name}}"
    from_email: "{{env.SMTP_FROM_EMAIL}}"
```

### 3. Complete Email Workflow
**File: `actions/email_workflow.ps`**

```yaml
type: action
name: email.workflow
description: "Complete email workflow: draft and send"
implementation: orchestration
enabled: true
effect: write
tags: [ai, email, workflow]

input_schema:
  to: {}          # Recipient email
  subject: {}     # Email subject hint
  context: {}     # Email context

output_schema:
  success: {}     # Overall success
  message_id: {}  # Email message ID
  draft: {}       # Email draft details

defaults:
  return_final_only: false  # Return all step outputs
  steps:
    - ref: email.draft
      with:
        to: "{{to}}"
        subject: "{{subject}}"
        context: "{{context}}"
    - ref: email.send
      with:
        to: "{{email.draft.to}}"
        subject: "{{email.draft.subject}}"
        body: "{{email.draft.body}}"
        from_name: "AI Assistant"
```

## CRM Schema Example

### Contact Schema
**File: `schemas/contact.ps`**

```yaml
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
  - PATCH /{id}
  - DELETE /{id}

add_to_top_nav: true
search:
  enabled: true
  label: "Contacts"

default_list_view:
  fields: [id, first_name, last_name, email, phone, title, created_at]
  sort_by: created_at
  sort_order: desc
  page_size: 25

fields:
  # Primary key
  - name: id
    view_name: ID
    type: string
    required: true
    primary_key: true
    system_managed: true

  # Basic information
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

  - name: title
    view_name: Job Title
    type: string
    required: false
    length: 100

  # Status and preferences
  - name: status
    view_name: Status
    type: picklist.excl
    required: false
    values: [active, inactive, prospect, customer]
    default: active

  - name: preferred_contact_method
    view_name: Preferred Contact Method
    type: picklist.excl
    required: false
    values: [email, phone, sms]
    default: email

  # Relationships
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

# Define relationships
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
    description: "Recent activities for this contact"
```

## 🎨 Layout Example

### Contact Layout
**File: `layouts/contact.ps`**

```yaml
type: layout
name: contact
add_to_global_nav: true
weight: 150
description: "Contact detail page layout"

components:
  # Main contact information
  - type: field_section
    name: basic_info
    view_name: Contact Information
    location: main
    layout: two_column
    fields:
      - first_name
      - last_name
      - name: email
        style_override:
          color: "#0070d2"
          font_weight: bold
      - phone
      - title
      - status

  # Account relationship
  - type: field_section
    name: account_info
    view_name: Account Information
    location: main
    layout: single_column
    fields:
      - account_id

  # Preferences
  - type: field_section
    name: preferences
    view_name: Preferences
    location: sidebar
    layout: single_column
    fields:
      - preferred_contact_method

  # Related activities
  - type: related_list
    name: contact_activities
    view_name: Recent Activities
    location: top_navigation
    data: activity
    limit: 10
    fields:
      - type
      - direction
      - status
      - outcome
      - created_at
    sort:
      field: created_at
      direction: desc

  # System information
  - type: field_section
    name: system_info
    view_name: System Information
    location: footer
    layout: two_column
    fields:
      - created_at
      - updated_at
```

## Automation Example

### Welcome Email Automation
**File: `automations/welcome_new_contact.ps`**

```yaml
type: automation
name: welcome_new_contact
description: "Send welcome email when new contact is created"
enabled: true

trigger:
  type: database_event
  on: record_created
  tables: [contact]
  
  # Only trigger for active contacts with email
  filters:
    status: "active"
    email: "!null"

action:
  ref: email.workflow
  with:
    to: "{{trigger.record.email}}"
    subject: "Welcome to our platform"
    context: |
      New contact: {{trigger.record.first_name}} {{trigger.record.last_name}}
      Email: {{trigger.record.email}}
      Title: {{trigger.record.title}}
      Created: {{trigger.record.created_at}}
```

## Integration Example

### Gmail SMTP Integration
**File: `integrations/gmail_smtp.ps`**

```yaml
type: integration
name: gmail_smtp
service: email
description: "Send emails via Gmail SMTP"

connection:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  use_tls: true
  timeout: 30

auth:
  type: basic_auth
  username_env: GMAIL_USERNAME
  password_env: GMAIL_APP_PASSWORD

# Map action inputs to SMTP parameters
request_mapping:
  to: "{{to}}"
  subject: "{{subject}}"
  body: "{{body}}"
  from_name: "{{from_name}}"
  from_email: "{{env.GMAIL_USERNAME}}"
  content_type: "text/plain"

# Map SMTP response to action output
response_mapping:
  success_condition: "smtp_response == 'success'"
  message_id: "{{smtp_message_id}}"

error_handling:
  on_failure: log_error
  retry_attempts: 3
  retry_delay: 5
  timeout: 30
```

## Form Example

### Contact Capture Form
**File: `content/forms/contact_capture.ps`**

```yaml
type: form
name: contact_capture_form
title: Contact Capture Form
description: "Capture new contact information"

# Target configuration
target_object: contact
action: upsert
match_conditions:
  - field: email
    value: "{form.email}"
    operator: iequals
on_no_match: create_new
on_multiple_matches: update_first
default_behavior: overwrite

# Messages
success_message: "Thank you! Your contact information has been submitted successfully."
error_message: "There was an error processing your submission. Please try again."

# Form fields
fields:
  - maps_to: contact.first_name
    label: First Name
    placeholder: "Enter your first name"
    required: true
    behavior: overwrite

  - maps_to: contact.last_name
    label: Last Name
    placeholder: "Enter your last name"
    required: true
    behavior: overwrite

  - maps_to: contact.email
    label: Email Address
    placeholder: "user@company.com"
    required: true
    behavior: overwrite
    validation:
      type: email
      message: "Please enter a valid email address"

  - maps_to: contact.phone
    label: Phone Number
    placeholder: "(555) 123-4567"
    required: false
    behavior: overwrite

  - maps_to: contact.title
    label: Job Title
    placeholder: "Your job title"
    required: false
    behavior: overwrite

  - maps_to: contact.preferred_contact_method
    label: Preferred Contact Method
    type: select
    options:
      - value: email
        label: Email
      - value: phone
        label: Phone
      - value: sms
        label: SMS
    default_value: email
    behavior: overwrite

# Embed configuration
embed:
  domains: ["*.yourdomain.com", "localhost"]
  style: "minimal"
  theme: "default"
  submit_button:
    label: "Submit Contact"
    style: "primary"
  css_overrides: |
    .form-container {
      max-width: 500px;
      margin: 0 auto;
      padding: 20px;
    }
```

## Search & AI Example

### Semantic Search Action
**File: `actions/search_contacts.ps`**

```yaml
type: action
name: search.contacts
description: "Search for contacts using semantic search"
implementation: search
enabled: true
effect: read
tags: [search, contacts]
embed: true

input_schema:
  query: {}       # Search query
  limit: {}       # Max results (optional)

output_schema:
  results: {}     # Search results
  count: {}       # Number of results

defaults:
  search_type: semantic
  target_objects: [contact]
  default_limit: 10
  fields: [first_name, last_name, email, title, phone]
  embedding_field: search_vector
```

### AI Contact Assistant
**File: `actions/contact_assistant.ps`**

```yaml
type: action
name: contact.assistant
description: "AI assistant for contact-related queries"
implementation: orchestration
enabled: true
effect: read
tags: [ai, assistant, contacts]
embed: true
when_to_use: "When user asks about contacts, people, or customer information"

input_schema:
  question: {}    # User's question
  context: {}     # Optional context

output_schema:
  answer: {}      # AI response
  contacts: {}    # Relevant contacts found
  suggestions: {} # Suggested next actions

defaults:
  return_final_only: true
  steps:
    # First, search for relevant contacts
    - ref: search.contacts
      with:
        query: "{{question}}"
        limit: 5
    
    # Then, use AI to provide helpful response
    - ref: contact.summarize
      with:
        question: "{{question}}"
        search_results: "{{search.contacts.results}}"
        context: "{{context}}"
```

### Contact Summarizer
**File: `actions/contact_summarize.ps`**

```yaml
type: action
name: contact.summarize
description: "Summarize contact search results with AI"
implementation: llm
enabled: true
effect: read
tags: [ai, summarize, contacts]

input_schema:
  question: {}        # Original question
  search_results: {}  # Search results to summarize
  context: {}         # Additional context

output_schema:
  answer: {}          # AI summary
  contacts: {}        # Structured contact data
  suggestions: {}     # Next action suggestions

defaults:
  system_prompt: |
    You are a helpful CRM assistant. Analyze contact search results and provide helpful summaries.
    
    Always:
    - Mention specific people by name
    - Highlight relevant details (title, company, contact info)
    - Suggest next actions (email, call, schedule meeting)
    - Be conversational and helpful
    
    Output JSON: {"answer":"...","contacts":[...],"suggestions":[...]}
    
  user_prompt: |
    User asked: {{question}}
    
    Search results: {{search_results}}
    Context: {{context}}
    
    Provide a helpful summary of the contacts found and suggest what the user might want to do next.
```

## Testing Example

### Contact Validation Test
**File: `tests/contact_validation.ps`**

```yaml
type: test
name: contact_validation_test
description: "Test contact creation and validation"
enabled: true

test_cases:
  - name: create_valid_contact
    description: "Create a contact with valid data"
    action: contact.create
    input:
      first_name: "John"
      last_name: "Doe"
      email: "john.doe@example.com"
      phone: "(555) 123-4567"
      status: "active"
    expected_output:
      success: true
    assertions:
      - field: id
        condition: not_null
      - field: email
        condition: equals
        value: "john.doe@example.com"

  - name: create_invalid_contact
    description: "Try to create contact with invalid email"
    action: contact.create
    input:
      first_name: "Jane"
      last_name: "Doe"
      email: "invalid-email"
    expected_output:
      success: false
    assertions:
      - field: error
        condition: contains
        value: "invalid email"
```

## Report Example

### Contact Report
**File: `reports/contacts_report.ps`**

```yaml
type: report
name: contacts_report
title: Contact List Report
description: Simple tabular report showing contact information
source: Contact

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

These examples demonstrate the full power and flexibility of the PlayScript language. Each file type serves a specific purpose in building comprehensive business applications with AI capabilities.
