"""
Tests for Protocol Buffer converter functionality.
"""

import pytest
from struct_mcp.converters.protobuf import ProtobufConverter


class TestProtobufConverter:
    """Test cases for ProtobufConverter."""

    def test_convert_simple_structure(self):
        """Test converting a simple structure to protobuf format."""
        structures = {
            "user_profile": {
                "description": "User profile information",
                "fields": {
                    "user_id": {
                        "type": "string",
                        "nullable": False,
                        "repeated": False,
                        "description": "Unique user identifier",
                    },
                    "age": {
                        "type": "integer",
                        "nullable": True,
                        "repeated": False,
                        "description": "User's age",
                    },
                    "tags": {
                        "type": "string",
                        "nullable": False,
                        "repeated": True,
                        "description": "User tags",
                    },
                },
            }
        }

        converter = ProtobufConverter()
        result = converter.convert(structures)

        # Check basic structure
        assert 'syntax = "proto3";' in result
        assert "package generated_schema;" in result
        assert "message UserProfile {" in result

        # Check field definitions
        assert "string user_id = 1;" in result
        assert "optional int32 age = 2;" in result
        assert "repeated string tags = 3;" in result

        # Check comments
        assert "// User profile information" in result
        assert "// Unique user identifier" in result
        assert "// User's age" in result
        assert "// User tags" in result

    def test_convert_multiple_structures(self):
        """Test converting multiple structures."""
        structures = {
            "user": {
                "fields": {
                    "name": {"type": "string", "nullable": False, "repeated": False}
                }
            },
            "product": {
                "fields": {
                    "price": {"type": "decimal", "nullable": False, "repeated": False}
                }
            },
        }

        converter = ProtobufConverter()
        result = converter.convert(structures)

        assert "message User {" in result
        assert "message Product {" in result
        assert "string name = 1;" in result
        assert "double price = 1;" in result

    def test_type_mapping(self):
        """Test that internal types are correctly mapped to protobuf types."""
        structures = {
            "type_test": {
                "fields": {
                    "string_field": {
                        "type": "string",
                        "nullable": False,
                        "repeated": False,
                    },
                    "integer_field": {
                        "type": "integer",
                        "nullable": False,
                        "repeated": False,
                    },
                    "decimal_field": {
                        "type": "decimal",
                        "nullable": False,
                        "repeated": False,
                    },
                    "boolean_field": {
                        "type": "boolean",
                        "nullable": False,
                        "repeated": False,
                    },
                    "unknown_field": {
                        "type": "unknown",
                        "nullable": False,
                        "repeated": False,
                    },
                }
            }
        }

        converter = ProtobufConverter()
        result = converter.convert(structures)

        # Check type mappings
        assert "string string_field = 1;" in result
        assert "int32 integer_field = 2;" in result
        assert "double decimal_field = 3;" in result
        assert "bool boolean_field = 4;" in result
        assert "string unknown_field = 5;" in result  # Unknown types default to string

    def test_pascal_case_conversion(self):
        """Test snake_case to PascalCase conversion."""
        converter = ProtobufConverter()

        assert converter._to_pascal_case("user_profile") == "UserProfile"
        assert converter._to_pascal_case("simple") == "Simple"
        assert converter._to_pascal_case("very_long_name_here") == "VeryLongNameHere"
        assert converter._to_pascal_case("") == ""

    def test_field_modifiers(self):
        """Test field modifiers (optional, repeated)."""
        structures = {
            "test": {
                "fields": {
                    "required_field": {
                        "type": "string",
                        "nullable": False,
                        "repeated": False,
                    },
                    "optional_field": {
                        "type": "string",
                        "nullable": True,
                        "repeated": False,
                    },
                    "repeated_field": {
                        "type": "string",
                        "nullable": False,
                        "repeated": True,
                    },
                    "optional_repeated": {
                        "type": "string",
                        "nullable": True,
                        "repeated": True,
                    },
                }
            }
        }

        converter = ProtobufConverter()
        result = converter.convert(structures)

        # Check modifiers
        assert "string required_field = 1;" in result  # No modifier
        assert "optional string optional_field = 2;" in result
        assert "repeated string repeated_field = 3;" in result
        assert (
            "repeated string optional_repeated = 4;" in result
        )  # repeated takes precedence

    def test_empty_structures(self):
        """Test handling empty or malformed structures."""
        converter = ProtobufConverter()

        # Empty structures
        result = converter.convert({})
        assert 'syntax = "proto3";' in result
        assert "package generated_schema;" in result

        # Structure without fields
        structures = {"empty_message": {"description": "Empty message"}}
        result = converter.convert(structures)
        assert "message EmptyMessage {" in result
        assert "}" in result

    def test_convert_cheese_catalog(self):
        """Test converting a realistic cheese catalog structure."""
        structures = {
            "cheese_inventory": {
                "description": "Artisanal cheese catalog with provenance tracking",
                "fields": {
                    "cheese_id": {
                        "type": "string",
                        "nullable": False,
                        "repeated": False,
                        "description": "Unique identifier for each cheese",
                    },
                    "stinkiness_level": {
                        "type": "integer",
                        "nullable": True,
                        "repeated": False,
                        "description": "Stinkiness rating from 1-10",
                    },
                    "tasting_notes": {
                        "type": "string",
                        "nullable": False,
                        "repeated": True,
                        "description": "Expert tasting descriptions",
                    },
                    "is_available": {
                        "type": "boolean",
                        "nullable": False,
                        "repeated": False,
                        "description": "Currently in stock",
                    },
                    "price_per_pound": {
                        "type": "decimal",
                        "nullable": True,
                        "repeated": False,
                        "description": "Current retail price",
                    },
                },
            }
        }

        converter = ProtobufConverter()
        result = converter.convert(structures)

        # Check overall structure
        assert "message CheeseInventory {" in result
        assert "// Artisanal cheese catalog with provenance tracking" in result

        # Check specific fields
        assert "string cheese_id = 1;" in result
        assert "optional int32 stinkiness_level = 2;" in result
        assert "repeated string tasting_notes = 3;" in result
        assert "bool is_available = 4;" in result
        assert "optional double price_per_pound = 5;" in result
