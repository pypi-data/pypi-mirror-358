# Struct-MCP

Transform data structure definitions into queryable MCP servers. Define your data structures with business context and get an AI-queryable interface that can answer questions about field meanings, data lineage, and structure.

## Quick Start

```bash
# Install
pip install struct-mcp

# Create a structure definition
echo "cheese_inventory:
  description: 'Artisanal cheese catalog'
  fields:
    cheese_id:
      type: string
      description: 'Unique identifier for each cheese'
      upstream_table: 'inventory.raw_cheese_data'
    name:
      type: string
      description: 'Display name of the cheese'
    stinkiness_level:
      type: integer
      nullable: true
      description: 'Stinkiness rating from 1-10'
" > cheese.yaml

# Start MCP server
struct-mcp serve cheese.yaml
```

## Supported Formats

Load from multiple input formats:

- **YAML** - Primary format with full business context
- **JSON Schema** - Standard JSON Schema files
- **OpenSearch** - Elasticsearch/OpenSearch mappings
- **Avro** - Apache Avro schemas
- **Pydantic** - Python BaseModel classes
- **Protocol Buffer** - .proto message definitions

```bash
struct-mcp serve schema.yaml        # YAML
struct-mcp serve schema.json        # JSON Schema/OpenSearch/Avro
struct-mcp serve model.py          # Pydantic
struct-mcp serve messages.proto    # Protocol Buffer
```

## What You Can Ask

Once loaded, query your structures with natural language:

- *"What does the cheese_id field represent?"*
- *"Which fields come from the inventory table?"*
- *"What fields are nullable and why?"*
- *"How is stinkiness_level calculated?"*
- *"Show me all array fields"*

## Python API

```python
from struct_mcp import StructMCP, MCPServer

# Load any format
smc = StructMCP.from_file("cheese.yaml")

# Query programmatically
fields = smc.get_fields("cheese_inventory")
nullable_fields = smc.get_fields("cheese_inventory", nullable=True)

# Convert between formats
opensearch_mapping = smc.to_opensearch()
pydantic_model = smc.to_pydantic()

# Start MCP server
server = MCPServer(smc)
server.start()
```

## Examples

See `examples/` for sample files in all supported formats:
- `cheese_catalog.yaml` - Artisanal cheese inventory
- `user_profiles.yaml` - User data with preferences
- `financial_transactions.yaml` - Payment processing metadata

## Documentation

For detailed setup, development, and API documentation, see [setup.md](setup.md).

## License

MIT
