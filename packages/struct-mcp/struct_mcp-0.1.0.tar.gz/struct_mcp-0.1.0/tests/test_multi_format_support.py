"""
Tests for multi-format support in StructMCP.
"""

import pytest
import json
from pathlib import Path
from struct_mcp import StructMCP


def test_from_file_yaml(tmp_path):
    """Test loading from YAML file using from_file."""
    yaml_content = """
cheese_inventory:
  description: "Test cheese catalog"
  fields:
    cheese_id:
      type: string
      nullable: false
      description: "Unique identifier"
"""

    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    struct_mcp = StructMCP.from_file(yaml_file)

    assert "cheese_inventory" in struct_mcp.structures
    assert "cheese_id" in struct_mcp.get_fields("cheese_inventory")


def test_from_file_yml_extension(tmp_path):
    """Test loading from .yml file using from_file."""
    yaml_content = """
test_structure:
  description: "Test with yml extension"
  fields:
    test_field:
      type: string
      nullable: false
"""

    yml_file = tmp_path / "test.yml"
    yml_file.write_text(yaml_content)

    struct_mcp = StructMCP.from_file(yml_file)

    assert "test_structure" in struct_mcp.structures


def test_from_file_json_schema(tmp_path):
    """Test loading from JSON Schema file using from_file."""
    schema_content = {
        "title": "test_inventory",
        "description": "Test schema",
        "type": "object",
        "properties": {"test_id": {"type": "string", "description": "Test identifier"}},
        "required": ["test_id"],
    }

    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps(schema_content, indent=2))

    struct_mcp = StructMCP.from_file(json_file)

    assert "test_inventory" in struct_mcp.structures
    assert "test_id" in struct_mcp.get_fields("test_inventory")


def test_from_file_opensearch_mapping(tmp_path):
    """Test loading from OpenSearch mapping file using from_file."""
    mapping_content = {
        "test_index": {
            "mappings": {
                "properties": {
                    "test_field": {"type": "text"},
                    "count_field": {"type": "integer"},
                }
            }
        }
    }

    json_file = tmp_path / "opensearch.json"
    json_file.write_text(json.dumps(mapping_content, indent=2))

    struct_mcp = StructMCP.from_file(json_file)

    assert "test_index" in struct_mcp.structures
    fields = struct_mcp.get_fields("test_index")
    assert "test_field" in fields
    assert "count_field" in fields
    assert fields["count_field"]["type"] == "integer"


def test_from_file_avro_schema(tmp_path):
    """Test loading from Avro schema file using from_file."""
    schema_content = {
        "type": "record",
        "name": "test_record",
        "doc": "Test Avro schema",
        "fields": [
            {"name": "test_field", "type": "string", "doc": "Test field"},
            {"name": "count_field", "type": "int", "doc": "Count field"},
        ],
    }

    json_file = tmp_path / "avro.json"
    json_file.write_text(json.dumps(schema_content, indent=2))

    struct_mcp = StructMCP.from_file(json_file)

    assert "test_record" in struct_mcp.structures
    fields = struct_mcp.get_fields("test_record")
    assert "test_field" in fields
    assert "count_field" in fields
    assert fields["count_field"]["type"] == "integer"


def test_from_file_pydantic_model(tmp_path):
    """Test loading from Pydantic model file using from_file."""
    model_content = '''
from typing import Optional
from pydantic import BaseModel, Field

class TestModel(BaseModel):
    """Test Pydantic model"""
    
    test_field: str = Field(description="Test field")
    count_field: int = Field(description="Count field")
    optional_field: Optional[str] = Field(description="Optional field")
'''

    py_file = tmp_path / "test_model.py"
    py_file.write_text(model_content)

    struct_mcp = StructMCP.from_file(py_file)

    assert "test_model" in struct_mcp.structures
    fields = struct_mcp.get_fields("test_model")
    assert "test_field" in fields
    assert "count_field" in fields
    assert "optional_field" in fields
    assert fields["optional_field"]["nullable"] == True


def test_from_file_unsupported_extension(tmp_path):
    """Test error handling for unsupported file extensions."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("some content")

    with pytest.raises(ValueError, match="Unsupported file format"):
        StructMCP.from_file(test_file)


def test_from_file_nonexistent_file():
    """Test error handling for non-existent files."""
    with pytest.raises(FileNotFoundError):
        StructMCP.from_file("nonexistent.yaml")


def test_format_detection_opensearch():
    """Test OpenSearch format detection."""
    # Should detect OpenSearch mapping
    opensearch_data = {
        "index1": {"mappings": {"properties": {"field": {"type": "text"}}}}
    }
    assert StructMCP._looks_like_opensearch(opensearch_data) == True

    # Should detect direct properties
    opensearch_data2 = {"index1": {"properties": {"field": {"type": "keyword"}}}}
    assert StructMCP._looks_like_opensearch(opensearch_data2) == True

    # Should not detect non-OpenSearch data
    other_data = {"type": "record", "fields": []}
    assert StructMCP._looks_like_opensearch(other_data) == False


def test_format_detection_avro():
    """Test Avro format detection."""
    # Should detect single Avro record
    avro_data = {"type": "record", "name": "test", "fields": []}
    assert StructMCP._looks_like_avro(avro_data) == True

    # Should detect array of Avro records
    avro_array = [
        {"type": "record", "name": "test1", "fields": []},
        {"type": "record", "name": "test2", "fields": []},
    ]
    assert StructMCP._looks_like_avro(avro_array) == True

    # Should not detect non-Avro data
    other_data = {"type": "object", "properties": {}}
    assert StructMCP._looks_like_avro(other_data) == False


def test_round_trip_conversions(tmp_path):
    """Test round-trip conversions between formats."""
    # Start with YAML
    yaml_content = """
test_structure:
  description: "Round trip test"
  fields:
    id_field:
      type: string
      nullable: false
      description: "ID field"
    count_field:
      type: integer
      nullable: true
      description: "Count field"
"""

    yaml_file = tmp_path / "original.yaml"
    yaml_file.write_text(yaml_content)

    # Load from YAML
    original = StructMCP.from_file(yaml_file)

    # Convert to other formats and save
    opensearch_json = original.to_opensearch()
    opensearch_file = tmp_path / "converted_opensearch.json"
    opensearch_file.write_text(opensearch_json)

    avro_json = original.to_avro()
    avro_file = tmp_path / "converted_avro.json"
    avro_file.write_text(avro_json)

    pydantic_py = original.to_pydantic()
    pydantic_file = tmp_path / "converted_pydantic.py"
    pydantic_file.write_text(pydantic_py)

    # Load back from converted formats
    from_opensearch = StructMCP.from_file(opensearch_file)
    from_avro = StructMCP.from_file(avro_file)
    from_pydantic = StructMCP.from_file(pydantic_file)

    # Check that all have the expected structure
    for struct_mcp in [from_opensearch, from_avro, from_pydantic]:
        structure_names = struct_mcp.get_structure_names()
        assert len(structure_names) > 0

        first_structure = structure_names[0]
        fields = struct_mcp.get_fields(first_structure)
        assert len(fields) > 0


def test_specific_format_methods():
    """Test that specific format methods still work."""
    # These methods should still be available for backward compatibility
    # and explicit format specification

    # Test that the methods exist and are callable
    assert hasattr(StructMCP, "from_yaml")
    assert hasattr(StructMCP, "from_json_schema")
    assert hasattr(StructMCP, "from_opensearch")
    assert hasattr(StructMCP, "from_avro")
    assert hasattr(StructMCP, "from_pydantic")

    # Methods should be callable (basic test)
    assert callable(StructMCP.from_yaml)
    assert callable(StructMCP.from_json_schema)
    assert callable(StructMCP.from_opensearch)
    assert callable(StructMCP.from_avro)
    assert callable(StructMCP.from_pydantic)
