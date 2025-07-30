"""
Tests for Protocol Buffer parser functionality.
"""

import pytest
from pathlib import Path
from struct_mcp.parsers.protobuf_parser import ProtobufParser


class TestProtobufParser:
    """Test cases for ProtobufParser."""

    def test_parse_simple_message(self, tmp_path):
        """Test parsing a simple protobuf message."""
        proto_content = """
        syntax = "proto3";
        
        message TestMessage {
            string name = 1;
            int32 age = 2;
            bool active = 3;
        }
        """

        proto_file = tmp_path / "test.proto"
        proto_file.write_text(proto_content)

        parser = ProtobufParser()
        result = parser.parse(proto_file)

        assert "TestMessage" in result
        message = result["TestMessage"]

        assert "fields" in message
        fields = message["fields"]

        # Check field parsing
        assert "name" in fields
        assert fields["name"]["type"] == "string"
        assert not fields["name"]["nullable"]
        assert not fields["name"]["repeated"]

        assert "age" in fields
        assert fields["age"]["type"] == "integer"

        assert "active" in fields
        assert fields["active"]["type"] == "boolean"

    def test_parse_optional_and_repeated_fields(self, tmp_path):
        """Test parsing optional and repeated fields."""
        proto_content = """
        syntax = "proto3";
        
        message TestMessage {
            optional string optional_field = 1;
            repeated string repeated_field = 2;
            string regular_field = 3;
        }
        """

        proto_file = tmp_path / "test.proto"
        proto_file.write_text(proto_content)

        parser = ProtobufParser()
        result = parser.parse(proto_file)

        fields = result["TestMessage"]["fields"]

        # Check optional field
        assert fields["optional_field"]["nullable"] == True
        assert fields["optional_field"]["repeated"] == False

        # Check repeated field
        assert fields["repeated_field"]["nullable"] == False
        assert fields["repeated_field"]["repeated"] == True

        # Check regular field
        assert fields["regular_field"]["nullable"] == False
        assert fields["regular_field"]["repeated"] == False

    def test_parse_multiple_messages(self, tmp_path):
        """Test parsing multiple messages in one file."""
        proto_content = """
        syntax = "proto3";
        
        message User {
            string name = 1;
            int32 age = 2;
        }
        
        message Product {
            string title = 1;
            double price = 2;
        }
        """

        proto_file = tmp_path / "test.proto"
        proto_file.write_text(proto_content)

        parser = ProtobufParser()
        result = parser.parse(proto_file)

        assert "User" in result
        assert "Product" in result

        # Check User message
        user_fields = result["User"]["fields"]
        assert "name" in user_fields
        assert "age" in user_fields

        # Check Product message
        product_fields = result["Product"]["fields"]
        assert "title" in product_fields
        assert "price" in product_fields
        assert product_fields["price"]["type"] == "decimal"

    def test_parse_with_comments(self, tmp_path):
        """Test parsing proto file with comments."""
        proto_content = """
        syntax = "proto3";
        
        // This is a test message
        message TestMessage {
            // User's name
            string name = 1;
            /* Multi-line
               comment */
            int32 age = 2;
        }
        """

        proto_file = tmp_path / "test.proto"
        proto_file.write_text(proto_content)

        parser = ProtobufParser()
        result = parser.parse(proto_file)

        # Should still parse correctly despite comments
        assert "TestMessage" in result
        fields = result["TestMessage"]["fields"]
        assert "name" in fields
        assert "age" in fields

    def test_type_mapping(self, tmp_path):
        """Test that proto types are correctly mapped to internal types."""
        proto_content = """
        syntax = "proto3";
        
        message TypeTest {
            double double_field = 1;
            float float_field = 2;
            int32 int32_field = 3;
            int64 int64_field = 4;
            uint32 uint32_field = 5;
            uint64 uint64_field = 6;
            sint32 sint32_field = 7;
            sint64 sint64_field = 8;
            fixed32 fixed32_field = 9;
            fixed64 fixed64_field = 10;
            sfixed32 sfixed32_field = 11;
            sfixed64 sfixed64_field = 12;
            bool bool_field = 13;
            string string_field = 14;
            bytes bytes_field = 15;
        }
        """

        proto_file = tmp_path / "test.proto"
        proto_file.write_text(proto_content)

        parser = ProtobufParser()
        result = parser.parse(proto_file)

        fields = result["TypeTest"]["fields"]

        # Test decimal types
        assert fields["double_field"]["type"] == "decimal"
        assert fields["float_field"]["type"] == "decimal"

        # Test integer types
        for field_name in [
            "int32_field",
            "int64_field",
            "uint32_field",
            "uint64_field",
            "sint32_field",
            "sint64_field",
            "fixed32_field",
            "fixed64_field",
            "sfixed32_field",
            "sfixed64_field",
        ]:
            assert fields[field_name]["type"] == "integer"

        # Test boolean
        assert fields["bool_field"]["type"] == "boolean"

        # Test string types
        assert fields["string_field"]["type"] == "string"
        assert fields["bytes_field"]["type"] == "string"

    def test_validation(self):
        """Test the validate method."""
        parser = ProtobufParser()

        # Valid data
        valid_data = {
            "TestMessage": {
                "description": "Test message",
                "fields": {
                    "name": {
                        "type": "string",
                        "nullable": False,
                        "repeated": False,
                        "description": "Name field",
                    }
                },
            }
        }

        assert parser.validate(valid_data) == True

        # Invalid data - missing required field properties
        invalid_data = {
            "TestMessage": {
                "fields": {
                    "name": {
                        "type": "string"
                        # Missing nullable and repeated
                    }
                }
            }
        }

        assert parser.validate(invalid_data) == False

        # Invalid data - not a dict
        assert parser.validate("not a dict") == False

    def test_file_not_found(self):
        """Test handling of non-existent files."""
        parser = ProtobufParser()

        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.proto")

    def test_empty_proto_file(self, tmp_path):
        """Test parsing an empty or malformed proto file."""
        proto_file = tmp_path / "empty.proto"
        proto_file.write_text("")

        parser = ProtobufParser()
        result = parser.parse(proto_file)

        # Should return empty dict for empty file
        assert result == {}

    def test_parse_cheese_catalog_example(self):
        """Test parsing the actual cheese catalog example file."""
        # Use the real example file if it exists
        example_path = (
            Path(__file__).parent.parent / "examples" / "cheese_catalog.proto"
        )

        if example_path.exists():
            parser = ProtobufParser()
            result = parser.parse(example_path)

            # Should have parsed messages
            assert len(result) > 0

            # Check for CheeseInventory message
            if "CheeseInventory" in result:
                cheese_fields = result["CheeseInventory"]["fields"]
                assert "cheese_id" in cheese_fields
                assert "name" in cheese_fields
        else:
            pytest.skip("Example cheese_catalog.proto file not found")
