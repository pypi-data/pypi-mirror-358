# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Struct-MCP is a Python package that transforms data structure definitions into queryable MCP servers. It supports multiple input formats (YAML, JSON Schema, OpenSearch mappings, Avro schemas, and Pydantic models) and creates an AI-queryable interface that can answer questions about field meanings, data lineage, and structure.

## Development Commands

```bash
# Setup development environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=struct_mcp

# Run specific test file  
pytest tests/test_struct_parser.py

# Run tests with verbose output
pytest -v

# Build package
uv build

# Validate build
twine check dist/*

# Start MCP server with example (supports multiple formats)
python -m struct_mcp serve examples/cheese_catalog.yaml
python -m struct_mcp serve examples/cheese_catalog.json
python -m struct_mcp serve examples/cheese_catalog_pydantic.py
python -m struct_mcp serve examples/cheese_catalog.proto

# Test MCP server with inspector tool
npx @modelcontextprotocol/inspector struct-mcp serve examples/cheese_catalog.yaml
```

## Architecture

### Package Structure
- **Package name**: `struct_mcp` (underscores for Python import)
- **CLI entry point**: `struct-mcp` (with commands: serve, validate, convert, docs)
- **Core modules**:
  - `cli.py` - CLI interface using argparse
  - `struct_parser.py` - Core structure parsing logic with multi-format support
  - `mcp_server.py` - MCP server implementation
  - `parsers/` - Modular parser system (yaml_parser.py, json_schema_parser.py, opensearch_parser.py, avro_parser.py, pydantic_parser.py, protobuf_parser.py)
  - `converters/` - Format conversion modules (opensearch.py, avro.py, pydantic.py, protobuf.py)

### Technical Stack
- Python 3.9+
- uv for package management
- pytest for testing with fixtures
- MCP Python library for server implementation
- Click for CLI interface
- PyYAML for YAML parsing

### Data Structure Formats
The project supports multiple formats for defining data structures with both technical and business context:

#### YAML Format (Primary)

```yaml
structure_name:
  description: "Business description"
  version: "1.0.0"
  business_owner: "Team Name"
  
  fields:
    field_name:
      type: string|integer|boolean|decimal
      nullable: true|false
      repeated: true|false  # for arrays
      description: "Field purpose and context"
      upstream_table: "source.table_name"
      calculation_logic: "How this field is derived"
      business_rules: "Business context and constraints"
```

#### Supported Input Formats
- **YAML** (.yaml, .yml) - Primary format with full business context support
- **JSON Schema** (.json) - Standard JSON Schema with custom business properties
- **OpenSearch Mappings** (.json) - Elasticsearch/OpenSearch index mappings
- **Avro Schemas** (.json) - Apache Avro record schemas
- **Pydantic Models** (.py) - Python Pydantic BaseModel classes
- **Protocol Buffer Schemas** (.proto) - Google Protocol Buffer message definitions

### MCP Server Capabilities
The MCP server can answer intelligent questions about data structures from any supported format:
- Field meanings and descriptions
- Data lineage (upstream tables)
- Calculation logic
- Business rules and constraints
- Type information and nullability
- Array/repeated field identification

## Key Implementation Notes

### Parser System
The parser system is modular and extensible:
- **YAMLParser** - Parse YAML structure definitions
- **JSONSchemaParser** - Parse JSON Schema files
- **OpenSearchParser** - Parse OpenSearch/Elasticsearch mappings
- **AvroParser** - Parse Avro schema files
- **PydanticParser** - Parse Python files with Pydantic BaseModel classes
- **ProtobufParser** - Parse Protocol Buffer (.proto) message definitions
- Each parser implements a common interface for consistent behavior

### Converters
Implement converters for common formats:
- OpenSearch mapping generation
- Avro schema generation  
- Pydantic model generation
- Protocol Buffer schema generation

### Testing Strategy
- Use pytest fixtures for test data
- Include comprehensive examples (cheese_catalog.yaml as primary example)
- Test both parsing and MCP server functionality
- Test format conversions

### CLI Design
Commands accept any supported file format:
- `struct-mcp serve <input_file>` - Start MCP server (auto-detects format)
- `struct-mcp validate <input_file>` - Validate format
- `struct-mcp convert <input_file> --to <format>` - Convert to other formats
- `struct-mcp docs <input_file> --output <file>` - Generate documentation

Supported input files: .yaml, .yml, .json (JSON Schema/OpenSearch/Avro), .py (Pydantic), .proto (Protocol Buffer)

## Example Usage Patterns

### Python API
```python
from struct_mcp import StructMCP, MCPServer

# Load from any supported format (auto-detection)
smc = StructMCP.from_file("cheese_catalog.yaml")
smc = StructMCP.from_file("schema.json")      # JSON Schema
smc = StructMCP.from_file("mapping.json")     # OpenSearch mapping
smc = StructMCP.from_file("model.py")         # Pydantic model
smc = StructMCP.from_file("messages.proto")   # Protocol Buffer

# Or use specific format methods
smc = StructMCP.from_yaml("cheese_catalog.yaml")
smc = StructMCP.from_json_schema("schema.json")
smc = StructMCP.from_opensearch("mapping.json")
smc = StructMCP.from_avro("schema.json")
smc = StructMCP.from_pydantic("model.py")
smc = StructMCP.from_protobuf("messages.proto")

# Query capabilities (same for all formats)
structure_names = smc.get_structure_names()
fields = smc.get_fields("structure_name")
field_info = smc.get_field("structure_name", "field_name")

# Format conversion (round-trip support)
opensearch_mapping = smc.to_opensearch()
avro_schema = smc.to_avro()
pydantic_model = smc.to_pydantic()
protobuf_schema = smc.to_protobuf()

# MCP server
server = MCPServer(smc)
server.start()
```

### Publication
Package is intended for PyPI publication as `struct-mcp` with proper pyproject.toml configuration using uv.
