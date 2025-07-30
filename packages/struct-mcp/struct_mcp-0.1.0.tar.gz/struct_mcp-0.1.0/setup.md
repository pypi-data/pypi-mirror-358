# Struct-MCP

A tool that transforms data structure definitions into queryable MCP servers. Define your data structures with business context, and instantly get an AI-queryable interface that can answer questions about field meanings, data lineage, and structure. Start with YAML, expand to any format.

## Quick Start

```bash
# Install the package
pip install struct-mcp

# Create your structure definition YAML file
echo "cheese_inventory:
  description: 'Artisanal cheese catalog with provenance tracking'
  fields:
    cheese_id:
      type: string
      nullable: false
      description: 'Unique identifier for each cheese'
      upstream_table: 'inventory.raw_cheese_data'
      calculation_logic: 'UUID generated at catalog entry'
    name:
      type: string
      nullable: false
      description: 'Display name of the cheese'
      upstream_table: 'suppliers.cheese_names'
      calculation_logic: 'Standardized from supplier catalogs'
    stinkiness_level:
      type: integer
      nullable: true
      repeated: false
      description: 'Stinkiness rating from 1-10'
      upstream_table: 'quality_control.assessments'
      calculation_logic: 'AVG(taster_ratings) WHERE category = stink'
    emoji:
      type: string
      nullable: false
      description: 'Visual representation for UI'
      calculation_logic: 'Default 🧀, custom per cheese type'
    origin_country:
      type: string
      nullable: true
      description: 'Country of origin'
      upstream_table: 'geography.cheese_origins'
      calculation_logic: 'Mapped from historical cheese records'
    tasting_notes:
      type: string
      nullable: true
      repeated: true
      description: 'Expert tasting descriptions'
      upstream_table: 'tastings.expert_reviews'
      calculation_logic: 'ARRAY_AGG(notes) GROUP BY cheese_id'
" > cheese_structure.yaml

# Start the MCP server
struct-mcp serve cheese_structure.yaml
```

## Project Setup

### Prerequisites
- Python 3.9+
- uv (for package management)

### Repository Structure
```
struct-mcp/
├── README.md
├── pyproject.toml
├── src/
│   └── struct_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── struct_parser.py
│       ├── mcp_server.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── yaml_parser.py
│       │   ├── json_schema_parser.py
│       │   ├── opensearch_parser.py
│       │   ├── avro_parser.py
│       │   ├── pydantic_parser.py
│       │   └── protobuf_parser.py
│       └── converters/
│           ├── __init__.py
│           ├── opensearch.py
│           ├── avro.py
│           ├── pydantic.py
│           └── protobuf.py
├── tests/
│   ├── __init__.py
│   ├── test_struct_parser.py
│   ├── test_mcp_server.py
│   └── fixtures/
│       ├── cheese_structure.yaml
│       └── sample_structure.yaml
└── examples/
    ├── cheese_catalog.yaml
    ├── cheese_catalog.json
    ├── cheese_catalog.proto
    ├── cheese_catalog_avro.json
    ├── cheese_catalog_opensearch.json
    ├── cheese_catalog_pydantic.py
    ├── user_profiles.yaml
    └── financial_transactions.yaml
```

### Development Setup

```bash
# Clone and setup
git clone <your-repo>
cd struct-mcp

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests
pytest

# Run cheese example
python -m struct_mcp serve examples/cheese_catalog.yaml
```

### Installation from PyPI

```bash
pip install struct-mcp
```

## Structure Definition Formats

Define your data structures with both technical and business context. Supports multiple input formats including YAML, JSON Schema, OpenSearch mappings, Avro schemas, Pydantic models, and Protocol Buffer schemas:

```yaml
# Structure name
cheese_inventory:
  # Optional top-level metadata
  description: "Artisanal cheese catalog with provenance tracking"
  version: "1.2.0"
  business_owner: "Cheese Operations Team"
  
  # Field definitions
  fields:
    cheese_id:
      # Technical properties
      type: string           # Data type
      nullable: false        # Can be null?
      repeated: false        # Is this an array/list?
      
      # Business context
      description: "Unique identifier for each cheese in catalog"
      upstream_table: "inventory.raw_cheese_data" 
      calculation_logic: "UUID generated at catalog entry time"
      business_owner: "Inventory Team"
      
    name:
      type: string
      nullable: false
      repeated: false
      description: "Display name of the cheese (e.g. 'Camembert', 'Stilton')"
      upstream_table: "suppliers.cheese_names"
      calculation_logic: "Standardized from supplier catalogs with quality checks"
      
    stinkiness_level:
      type: integer
      nullable: true
      repeated: false
      description: "Stinkiness rating from 1-10 (10 = most pungent)"
      upstream_table: "quality_control.assessments"
      calculation_logic: "AVG(taster_ratings) WHERE assessment_type = 'aroma'"
      business_rules: "Only assessed for aged cheeses, null for fresh varieties"
      
    emoji:
      type: string
      nullable: false
      repeated: false
      description: "Visual representation for UI display"
      upstream_table: "ui_config.cheese_icons"
      calculation_logic: "Default 🧀, custom mappings per cheese type"
      
    origin_country:
      type: string
      nullable: true
      repeated: false
      description: "Country where this cheese style originated"
      upstream_table: "geography.cheese_origins"
      calculation_logic: "Historical mapping from cheese style to country"
      
    tasting_notes:
      type: string
      nullable: true
      repeated: true         # Array of tasting notes
      description: "Expert sommelier tasting descriptions"
      upstream_table: "tastings.expert_reviews"
      calculation_logic: "ARRAY_AGG(notes) GROUP BY cheese_id WHERE expert_level >= 3"
      
    is_available:
      type: boolean
      nullable: false
      repeated: false
      description: "Currently in stock and available for purchase"
      upstream_table: "inventory.current_stock"
      calculation_logic: "stock_quantity > 0 AND expiry_date > CURRENT_DATE"
      
    price_per_pound:
      type: decimal
      nullable: true
      repeated: false
      description: "Current retail price per pound in USD"
      upstream_table: "pricing.current_rates"
      calculation_logic: "Latest price from pricing engine with markup applied"
      business_rules: "Null for cheeses sold by piece rather than weight"
```

### Pydantic Model Support

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class CheeseInventory(BaseModel):
    """Artisanal cheese catalog with provenance tracking"""
    
    cheese_id: str = Field(description="Unique identifier for each cheese")
    name: str = Field(description="Display name of the cheese")
    stinkiness_level: Optional[int] = Field(description="Stinkiness rating from 1-10")
    emoji: str = Field(description="Visual representation for UI")
    origin_country: Optional[str] = Field(description="Country of origin")
    tasting_notes: Optional[List[str]] = Field(description="Expert tasting descriptions")
    is_available: bool = Field(description="Currently in stock and available for purchase")
    price_per_pound: Optional[float] = Field(description="Current retail price per pound in USD")
```

## MCP Server Capabilities

Once your YAML is loaded, the MCP server can answer questions like:

- **"What does the cheese_id field represent?"**
  → "Unique identifier for each cheese in catalog, UUID generated at catalog entry time from inventory.raw_cheese_data table"

- **"Which fields come from the inventory table?"** 
  → Lists all fields with `upstream_table` containing "inventory"

- **"What fields are arrays in this data?"**
  → Lists all fields where `repeated: true` (like tasting_notes)

- **"How is stinkiness_level calculated?"**
  → "AVG(taster_ratings) WHERE assessment_type = 'aroma' from quality_control.assessments table"

- **"Show me all nullable boolean fields"**
  → Lists fields matching `type: boolean` and `nullable: true`

- **"What cheese fields can be null and why?"**
  → "stinkiness_level (only assessed for aged cheeses), origin_country (some cheeses have unclear origins), price_per_pound (sold by piece not weight)"

- **"Tell me about the cheese emoji field"**
  → "Visual representation for UI display, defaults to 🧀 with custom mappings per cheese type from ui_config.cheese_icons"

## CLI Usage

```bash
# Start MCP server for a structure definition file
struct-mcp serve cheese_catalog.yaml

# Validate structure format
struct-mcp validate cheese_catalog.yaml

# Convert to other formats
struct-mcp convert cheese_catalog.yaml --to opensearch
struct-mcp convert cheese_catalog.yaml --to avro
struct-mcp convert cheese_catalog.yaml --to pydantic
struct-mcp convert cheese_catalog.yaml --to protobuf

# Generate documentation
struct-mcp docs cheese_catalog.yaml --output cheese_docs.md

# Support for multiple input formats
struct-mcp serve cheese_catalog_pydantic.py  # Pydantic models
struct-mcp serve schema.json                 # JSON Schema
struct-mcp serve mapping.json                # OpenSearch mappings  
struct-mcp serve schema.avro                 # Avro schemas
struct-mcp serve messages.proto              # Protocol Buffer schemas
```

## Python API

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

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=struct_mcp

# Run specific test file
pytest tests/test_struct_parser.py

# Run tests with verbose output
pytest -v
```

## Building and Publishing

```bash
# Build the package
uv build

# Check the build
twine check dist/*

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Examples

See the `examples/` directory for:
- **cheese_catalog.yaml**: Artisanal cheese inventory with stinkiness ratings and provenance
- **user_profiles.yaml**: User data with preferences and behavioral tracking  
- **financial_transactions.yaml**: Payment processing with fraud detection metadata
