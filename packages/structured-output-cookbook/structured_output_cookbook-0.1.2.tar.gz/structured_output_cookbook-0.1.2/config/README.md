# Custom YAML Schema Configuration

This directory contains YAML schema files for custom data extraction. Each YAML file defines both the extraction schema and the system prompt in a single, organized format.

## Schema Structure

Each YAML schema file must contain the following required fields:

```yaml
# Schema metadata
name: "Schema Name"
description: "Brief description of what this schema extracts"

# System prompt for the LLM
system_prompt: |
  Detailed instructions for the LLM on how to extract data.
  This can be multiple lines and should provide clear guidance
  on what information to look for and how to handle edge cases.

# JSON Schema definition
schema:
  type: object
  properties:
    field_name:
      type: string
      description: "Description of this field"
    # Add more properties as needed
  required: ["field_name"]
  additionalProperties: false
```

## Available Commands

### List Available Custom Schemas
```bash
structured-output list-schemas
```

### Extract Using Custom YAML Schema
```bash
structured-output extract-custom SCHEMA_NAME --text "Your text here"
```

Or from a file:
```bash
structured-output extract-custom SCHEMA_NAME --input-file input.txt
```

### Save Results
```bash
structured-output extract-custom SCHEMA_NAME --input-file input.txt --output results.json
```

### List Predefined Templates
```bash
structured-output list-templates
```

### Extract Using Predefined Template
```bash
structured-output extract job --text "Your job description here"
structured-output extract recipe --text "Your recipe text here"
```

## Example Usage

1. Create a new YAML schema file in this directory (e.g., `my_schema.yaml`)
2. Define your schema structure following the format above
3. List available schemas: `structured-output list-schemas`
4. Use your schema: `structured-output extract-custom my_schema --text "Sample text"`

## Pre-built Custom Schemas

The following example schemas are included:

- `news_article.yaml` - Extract structured information from news articles
- `product_review.yaml` - Extract structured information from product reviews  
- `customer_support.yaml` - Extract structured information from support tickets

## Schema Validation

The system automatically validates:
- Required fields (name, description, system_prompt, schema)
- JSON schema structure (must be type: object with properties)
- YAML syntax correctness

## Configuration Options

- `--config-dir`: Specify a different directory for YAML schemas (default: `config/schemas`)
- `--pretty`: Pretty print JSON output
- `--no-save`: Don't save results to file, only print to stdout
- `--output`: Specify custom output file path 