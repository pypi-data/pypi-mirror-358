"""
Tests for structure parser.
"""

import pytest
from struct_mcp.struct_parser import StructMCP


@pytest.fixture
def sample_structure():
    """Sample structure data for testing."""
    return {
        "cheese_inventory": {
            "description": "Artisanal cheese catalog",
            "fields": {
                "cheese_id": {
                    "type": "string",
                    "nullable": False,
                    "description": "Unique identifier",
                },
                "name": {
                    "type": "string",
                    "nullable": False,
                    "description": "Cheese name",
                },
                "stinkiness_level": {
                    "type": "integer",
                    "nullable": True,
                    "description": "Stinkiness rating 1-10",
                },
                "tasting_notes": {
                    "type": "string",
                    "nullable": True,
                    "repeated": True,
                    "description": "Expert tasting notes",
                },
            },
        }
    }


def test_struct_mcp_initialization(sample_structure):
    """Test StructMCP initialization."""
    struct_mcp = StructMCP(sample_structure)
    assert struct_mcp.structures == sample_structure


def test_get_structure_names(sample_structure):
    """Test getting structure names."""
    struct_mcp = StructMCP(sample_structure)
    names = struct_mcp.get_structure_names()
    assert names == ["cheese_inventory"]


def test_get_structure(sample_structure):
    """Test getting a specific structure."""
    struct_mcp = StructMCP(sample_structure)
    structure = struct_mcp.get_structure("cheese_inventory")
    assert structure == sample_structure["cheese_inventory"]

    # Test non-existent structure
    assert struct_mcp.get_structure("nonexistent") is None


def test_get_fields(sample_structure):
    """Test getting all fields."""
    struct_mcp = StructMCP(sample_structure)
    fields = struct_mcp.get_fields("cheese_inventory")
    assert "cheese_id" in fields
    assert "name" in fields
    assert "stinkiness_level" in fields
    assert "tasting_notes" in fields


def test_get_field(sample_structure):
    """Test getting a specific field."""
    struct_mcp = StructMCP(sample_structure)
    field = struct_mcp.get_field("cheese_inventory", "cheese_id")
    assert field["type"] == "string"
    assert field["nullable"] is False

    # Test non-existent field
    assert struct_mcp.get_field("cheese_inventory", "nonexistent") is None


def test_find_fields_with_property(sample_structure):
    """Test finding fields with specific properties."""
    struct_mcp = StructMCP(sample_structure)

    # Find nullable fields
    nullable_fields = struct_mcp.find_fields_with_property(
        "cheese_inventory", "nullable", True
    )
    assert "stinkiness_level" in nullable_fields
    assert "tasting_notes" in nullable_fields
    assert "cheese_id" not in nullable_fields

    # Find string fields
    string_fields = struct_mcp.find_fields_with_property(
        "cheese_inventory", "type", "string"
    )
    assert "cheese_id" in string_fields
    assert "name" in string_fields
    assert "tasting_notes" in string_fields


def test_find_fields_by_pattern(sample_structure):
    """Test finding fields by pattern in property values."""
    struct_mcp = StructMCP(sample_structure)

    # Find fields with 'rating' in description
    rating_fields = struct_mcp.find_fields_by_pattern(
        "cheese_inventory", "description", "rating"
    )
    assert "stinkiness_level" in rating_fields
    assert "cheese_id" not in rating_fields


def test_generate_docs(sample_structure):
    """Test documentation generation."""
    struct_mcp = StructMCP(sample_structure)
    docs = struct_mcp.generate_docs()

    assert "# cheese_inventory" in docs
    assert "Artisanal cheese catalog" in docs
    assert "### cheese_id" in docs
    assert "Unique identifier" in docs
