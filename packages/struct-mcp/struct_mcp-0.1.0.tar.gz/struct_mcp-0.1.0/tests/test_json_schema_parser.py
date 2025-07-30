"""
Tests for JSON Schema parser.
"""

import pytest
import json
from pathlib import Path
from struct_mcp.parsers.json_schema_parser import JSONSchemaParser


def test_json_schema_parser_valid_file(tmp_path):
    """Test parsing a valid JSON Schema file."""
    schema_content = {
        "title": "cheese_inventory",
        "description": "Artisanal cheese catalog",
        "type": "object",
        "properties": {
            "cheese_id": {"type": "string", "description": "Unique identifier"},
            "name": {"type": "string", "description": "Cheese name"},
            "stinkiness_level": {"type": "integer", "description": "Rating from 1-10"},
            "is_available": {"type": "boolean", "description": "In stock"},
            "tasting_notes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Expert reviews",
            },
        },
        "required": ["cheese_id", "name", "is_available"],
    }

    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = JSONSchemaParser()
    result = parser.parse(schema_file)

    assert "cheese_inventory" in result
    assert "fields" in result["cheese_inventory"]
    assert "cheese_id" in result["cheese_inventory"]["fields"]

    # Check field properties
    cheese_id_field = result["cheese_inventory"]["fields"]["cheese_id"]
    assert cheese_id_field["type"] == "string"
    assert cheese_id_field["nullable"] == False  # Required field
    assert cheese_id_field["repeated"] == False

    # Check array field
    tasting_notes_field = result["cheese_inventory"]["fields"]["tasting_notes"]
    assert tasting_notes_field["type"] == "string"
    assert tasting_notes_field["repeated"] == True
    assert tasting_notes_field["nullable"] == True  # Not in required list


def test_json_schema_parser_definitions(tmp_path):
    """Test parsing JSON Schema with definitions."""
    schema_content = {
        "$defs": {
            "cheese_inventory": {
                "type": "object",
                "description": "Cheese catalog",
                "properties": {
                    "cheese_id": {"type": "string", "description": "Unique ID"}
                },
            },
            "supplier_info": {
                "type": "object",
                "description": "Supplier details",
                "properties": {
                    "supplier_name": {
                        "type": "string",
                        "description": "Name of supplier",
                    }
                },
            },
        }
    }

    schema_file = tmp_path / "test_defs.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = JSONSchemaParser()
    result = parser.parse(schema_file)

    assert "cheese_inventory" in result
    assert "supplier_info" in result
    assert "fields" in result["cheese_inventory"]
    assert "cheese_id" in result["cheese_inventory"]["fields"]


def test_json_schema_parser_nonexistent_file():
    """Test parsing a non-existent file."""
    parser = JSONSchemaParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.json")


def test_json_schema_parser_invalid_json(tmp_path):
    """Test parsing invalid JSON."""
    invalid_content = '{"invalid": json, "missing": "quote}'

    schema_file = tmp_path / "invalid.json"
    schema_file.write_text(invalid_content)

    parser = JSONSchemaParser()

    with pytest.raises(ValueError):
        parser.parse(schema_file)


def test_json_schema_parser_union_types(tmp_path):
    """Test parsing JSON Schema with union types."""
    schema_content = {
        "title": "test_structure",
        "type": "object",
        "properties": {
            "nullable_field": {
                "type": ["string", "null"],
                "description": "Can be string or null",
            },
            "multi_type": {
                "type": ["string", "integer"],
                "description": "String or number",
            },
        },
    }

    schema_file = tmp_path / "union_types.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = JSONSchemaParser()
    result = parser.parse(schema_file)

    # Check nullable field
    nullable_field = result["test_structure"]["fields"]["nullable_field"]
    assert nullable_field["nullable"] == True
    assert nullable_field["type"] == "string"

    # Check multi-type field
    multi_field = result["test_structure"]["fields"]["multi_type"]
    assert multi_field["type"] == "string"  # Should take first non-null type


def test_json_schema_parser_validation():
    """Test validation method."""
    parser = JSONSchemaParser()

    # Valid data
    valid_data = {"structure1": {"fields": {"field1": {"type": "string"}}}}
    assert parser.validate(valid_data) == True

    # Invalid data
    assert parser.validate("not a dict") == False
    assert parser.validate({}) == True  # Empty is valid
