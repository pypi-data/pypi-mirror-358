"""
Tests for Avro schema parser.
"""

import pytest
import json
from pathlib import Path
from struct_mcp.parsers.avro_parser import AvroParser


def test_avro_parser_valid_schema(tmp_path):
    """Test parsing a valid Avro schema file."""
    schema_content = {
        "type": "record",
        "name": "cheese_inventory",
        "doc": "Artisanal cheese catalog",
        "fields": [
            {"name": "cheese_id", "type": "string", "doc": "Unique identifier"},
            {"name": "name", "type": "string", "doc": "Cheese name"},
            {
                "name": "stinkiness_level",
                "type": ["null", "int"],
                "doc": "Rating from 1-10",
            },
            {"name": "is_available", "type": "boolean", "doc": "In stock"},
            {
                "name": "tasting_notes",
                "type": ["null", {"type": "array", "items": "string"}],
                "doc": "Expert reviews",
            },
        ],
    }

    schema_file = tmp_path / "test_schema.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = AvroParser()
    result = parser.parse(schema_file)

    assert "cheese_inventory" in result
    assert "fields" in result["cheese_inventory"]
    assert "cheese_id" in result["cheese_inventory"]["fields"]

    # Check field properties
    cheese_id_field = result["cheese_inventory"]["fields"]["cheese_id"]
    assert cheese_id_field["type"] == "string"
    assert cheese_id_field["nullable"] == False
    assert cheese_id_field["repeated"] == False

    # Check nullable field
    stinkiness_field = result["cheese_inventory"]["fields"]["stinkiness_level"]
    assert stinkiness_field["type"] == "integer"
    assert stinkiness_field["nullable"] == True

    # Check array field
    tasting_notes_field = result["cheese_inventory"]["fields"]["tasting_notes"]
    assert tasting_notes_field["type"] == "string"
    assert tasting_notes_field["repeated"] == True
    assert tasting_notes_field["nullable"] == True


def test_avro_parser_array_of_schemas(tmp_path):
    """Test parsing Avro file with array of schemas."""
    schema_content = [
        {
            "type": "record",
            "name": "cheese_inventory",
            "doc": "Cheese catalog",
            "fields": [{"name": "cheese_id", "type": "string", "doc": "Unique ID"}],
        },
        {
            "type": "record",
            "name": "supplier_info",
            "doc": "Supplier details",
            "fields": [
                {"name": "supplier_name", "type": "string", "doc": "Name of supplier"}
            ],
        },
    ]

    schema_file = tmp_path / "array_schema.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = AvroParser()
    result = parser.parse(schema_file)

    assert "cheese_inventory" in result
    assert "supplier_info" in result
    assert "fields" in result["cheese_inventory"]
    assert "fields" in result["supplier_info"]


def test_avro_parser_nonexistent_file():
    """Test parsing a non-existent file."""
    parser = AvroParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.json")


def test_avro_parser_invalid_json(tmp_path):
    """Test parsing invalid JSON."""
    invalid_content = '{"invalid": json, "missing": "quote}'

    schema_file = tmp_path / "invalid.json"
    schema_file.write_text(invalid_content)

    parser = AvroParser()

    with pytest.raises(ValueError):
        parser.parse(schema_file)


def test_avro_parser_type_mappings(tmp_path):
    """Test Avro type to internal type mappings."""
    schema_content = {
        "type": "record",
        "name": "test_types",
        "fields": [
            {"name": "string_field", "type": "string"},
            {"name": "int_field", "type": "int"},
            {"name": "long_field", "type": "long"},
            {"name": "float_field", "type": "float"},
            {"name": "double_field", "type": "double"},
            {"name": "boolean_field", "type": "boolean"},
            {"name": "bytes_field", "type": "bytes"},
            {"name": "null_field", "type": "null"},
            {"name": "unknown_field", "type": "unknown_type"},
        ],
    }

    schema_file = tmp_path / "type_test.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = AvroParser()
    result = parser.parse(schema_file)

    fields = result["test_types"]["fields"]

    assert fields["string_field"]["type"] == "string"
    assert fields["int_field"]["type"] == "integer"
    assert fields["long_field"]["type"] == "integer"
    assert fields["float_field"]["type"] == "decimal"
    assert fields["double_field"]["type"] == "decimal"
    assert fields["boolean_field"]["type"] == "boolean"
    assert fields["bytes_field"]["type"] == "string"
    assert fields["null_field"]["type"] == "string"
    assert fields["unknown_field"]["type"] == "string"  # Default fallback


def test_avro_parser_complex_types(tmp_path):
    """Test parsing complex Avro types."""
    schema_content = {
        "type": "record",
        "name": "complex_types",
        "fields": [
            {"name": "simple_array", "type": {"type": "array", "items": "string"}},
            {
                "name": "nullable_array",
                "type": ["null", {"type": "array", "items": "int"}],
            },
            {
                "name": "nested_record",
                "type": {
                    "type": "record",
                    "name": "nested",
                    "fields": [{"name": "nested_field", "type": "string"}],
                },
            },
        ],
    }

    schema_file = tmp_path / "complex_test.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = AvroParser()
    result = parser.parse(schema_file)

    fields = result["complex_types"]["fields"]

    # Simple array
    assert fields["simple_array"]["type"] == "string"
    assert fields["simple_array"]["repeated"] == True
    assert fields["simple_array"]["nullable"] == False

    # Nullable array
    assert fields["nullable_array"]["type"] == "integer"
    assert fields["nullable_array"]["repeated"] == True
    assert fields["nullable_array"]["nullable"] == True

    # Nested record (treated as string for now)
    assert fields["nested_record"]["type"] == "string"
    assert fields["nested_record"]["repeated"] == False


def test_avro_parser_invalid_schema_format(tmp_path):
    """Test parsing invalid Avro schema format."""
    schema_content = {"type": "not_a_record", "name": "invalid"}

    schema_file = tmp_path / "invalid_schema.json"
    schema_file.write_text(json.dumps(schema_content, indent=2))

    parser = AvroParser()

    with pytest.raises(ValueError):
        parser.parse(schema_file)


def test_avro_parser_validation():
    """Test validation method."""
    parser = AvroParser()

    # Valid data
    valid_data = {"structure1": {"fields": {"field1": {"type": "string"}}}}
    assert parser.validate(valid_data) == True

    # Invalid data
    assert parser.validate("not a dict") == False
    assert parser.validate({}) == True  # Empty is valid
