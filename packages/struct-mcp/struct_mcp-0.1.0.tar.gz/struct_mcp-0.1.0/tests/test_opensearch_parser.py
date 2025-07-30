"""
Tests for OpenSearch mapping parser.
"""

import pytest
import json
from pathlib import Path
from struct_mcp.parsers.opensearch_parser import OpenSearchParser


def test_opensearch_parser_valid_mapping(tmp_path):
    """Test parsing a valid OpenSearch mapping file."""
    mapping_content = {
        "cheese_inventory": {
            "mappings": {
                "properties": {
                    "cheese_id": {
                        "type": "text",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
                    },
                    "name": {"type": "text"},
                    "stinkiness_level": {"type": "integer"},
                    "is_available": {"type": "boolean"},
                    "price_per_pound": {"type": "double"},
                }
            }
        }
    }

    mapping_file = tmp_path / "test_mapping.json"
    mapping_file.write_text(json.dumps(mapping_content, indent=2))

    parser = OpenSearchParser()
    result = parser.parse(mapping_file)

    assert "cheese_inventory" in result
    assert "fields" in result["cheese_inventory"]
    assert "cheese_id" in result["cheese_inventory"]["fields"]

    # Check field mappings
    cheese_id_field = result["cheese_inventory"]["fields"]["cheese_id"]
    assert cheese_id_field["type"] == "string"  # text maps to string
    assert cheese_id_field["nullable"] == True
    assert cheese_id_field["repeated"] == False

    stinkiness_field = result["cheese_inventory"]["fields"]["stinkiness_level"]
    assert stinkiness_field["type"] == "integer"

    price_field = result["cheese_inventory"]["fields"]["price_per_pound"]
    assert price_field["type"] == "decimal"  # double maps to decimal


def test_opensearch_parser_direct_properties(tmp_path):
    """Test parsing OpenSearch mapping with direct properties."""
    mapping_content = {
        "my_index": {
            "properties": {
                "title": {"type": "text", "description": "Document title"},
                "count": {"type": "integer"},
                "active": {"type": "boolean"},
            }
        }
    }

    mapping_file = tmp_path / "direct_props.json"
    mapping_file.write_text(json.dumps(mapping_content, indent=2))

    parser = OpenSearchParser()
    result = parser.parse(mapping_file)

    assert "my_index" in result
    assert "fields" in result["my_index"]
    assert len(result["my_index"]["fields"]) == 3


def test_opensearch_parser_multiple_structures(tmp_path):
    """Test parsing multiple OpenSearch mappings."""
    mapping_content = {
        "cheese_inventory": {
            "mappings": {"properties": {"cheese_id": {"type": "keyword"}}}
        },
        "supplier_info": {
            "mappings": {"properties": {"supplier_name": {"type": "text"}}}
        },
    }

    mapping_file = tmp_path / "multiple.json"
    mapping_file.write_text(json.dumps(mapping_content, indent=2))

    parser = OpenSearchParser()
    result = parser.parse(mapping_file)

    assert "cheese_inventory" in result
    assert "supplier_info" in result
    assert "fields" in result["cheese_inventory"]
    assert "fields" in result["supplier_info"]


def test_opensearch_parser_nonexistent_file():
    """Test parsing a non-existent file."""
    parser = OpenSearchParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.json")


def test_opensearch_parser_invalid_json(tmp_path):
    """Test parsing invalid JSON."""
    invalid_content = '{"invalid": json, "missing": "quote}'

    mapping_file = tmp_path / "invalid.json"
    mapping_file.write_text(invalid_content)

    parser = OpenSearchParser()

    with pytest.raises(ValueError):
        parser.parse(mapping_file)


def test_opensearch_parser_type_mappings(tmp_path):
    """Test OpenSearch type to internal type mappings."""
    mapping_content = {
        "test_types": {
            "mappings": {
                "properties": {
                    "text_field": {"type": "text"},
                    "keyword_field": {"type": "keyword"},
                    "integer_field": {"type": "integer"},
                    "long_field": {"type": "long"},
                    "double_field": {"type": "double"},
                    "float_field": {"type": "float"},
                    "boolean_field": {"type": "boolean"},
                    "date_field": {"type": "date"},
                    "unknown_field": {"type": "unknown_type"},
                }
            }
        }
    }

    mapping_file = tmp_path / "type_test.json"
    mapping_file.write_text(json.dumps(mapping_content, indent=2))

    parser = OpenSearchParser()
    result = parser.parse(mapping_file)

    fields = result["test_types"]["fields"]

    assert fields["text_field"]["type"] == "string"
    assert fields["keyword_field"]["type"] == "string"
    assert fields["integer_field"]["type"] == "integer"
    assert fields["long_field"]["type"] == "integer"
    assert fields["double_field"]["type"] == "decimal"
    assert fields["float_field"]["type"] == "decimal"
    assert fields["boolean_field"]["type"] == "boolean"
    assert fields["date_field"]["type"] == "string"
    assert fields["unknown_field"]["type"] == "string"  # Default fallback


def test_opensearch_parser_validation():
    """Test validation method."""
    parser = OpenSearchParser()

    # Valid data
    valid_data = {"structure1": {"fields": {"field1": {"type": "string"}}}}
    assert parser.validate(valid_data) == True

    # Invalid data
    assert parser.validate("not a dict") == False
    assert parser.validate({}) == True  # Empty is valid
