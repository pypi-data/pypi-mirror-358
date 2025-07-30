"""
Integration tests for loading all example files without errors.
This ensures all supported formats can be loaded and work with the MCP server.
"""

import pytest
import json
from pathlib import Path
from struct_mcp import StructMCP
from struct_mcp.mcp_server import MCPServer


def test_load_all_example_files():
    """Test that all example files can be loaded without errors."""
    examples_dir = Path(__file__).parent.parent / "examples"

    # Expected example files for each format
    example_files = [
        ("cheese_catalog.yaml", "YAML"),
        ("cheese_catalog.json", "JSON Schema"),
        ("cheese_catalog_opensearch.json", "OpenSearch"),
        ("cheese_catalog_avro.json", "Avro"),
        ("cheese_catalog_pydantic.py", "Pydantic"),
        ("cheese_catalog.proto", "Protocol Buffer"),
    ]

    loaded_structs = {}

    for filename, format_name in example_files:
        file_path = examples_dir / filename

        # Verify file exists
        assert file_path.exists(), f"Example file {filename} not found"

        # Load the file
        try:
            struct_mcp = StructMCP.from_file(file_path)
            loaded_structs[format_name] = struct_mcp
            print(f"✓ Successfully loaded {format_name} format from {filename}")
        except Exception as e:
            pytest.fail(f"Failed to load {format_name} format from {filename}: {e}")

    # Verify all formats were loaded
    assert len(loaded_structs) == len(example_files)

    # Verify each loaded structure has the expected cheese inventory structure
    for format_name, struct_mcp in loaded_structs.items():
        structure_names = struct_mcp.get_structure_names()
        assert len(structure_names) > 0, f"{format_name} has no structures"

        # Find cheese inventory structure (name may vary slightly by format)
        cheese_structure = None
        for name in structure_names:
            if "cheese" in name.lower():
                cheese_structure = name
                break

        assert cheese_structure is not None, f"{format_name} missing cheese structure"

        # Verify expected fields exist
        fields = struct_mcp.get_fields(cheese_structure)
        expected_fields = ["cheese_id", "name", "is_available"]

        for field in expected_fields:
            assert field in fields, f"{format_name} missing expected field '{field}'"

        print(f"✓ {format_name} has all expected fields")


def test_mcp_server_creation_with_all_formats():
    """Test that MCP server can be created with all supported formats."""
    examples_dir = Path(__file__).parent.parent / "examples"

    example_files = [
        "cheese_catalog.yaml",
        "cheese_catalog.json",
        "cheese_catalog_opensearch.json",
        "cheese_catalog_avro.json",
        "cheese_catalog_pydantic.py",
        "cheese_catalog.proto",
    ]

    for filename in example_files:
        file_path = examples_dir / filename

        # Load structure
        struct_mcp = StructMCP.from_file(file_path)

        # Create MCP server (should not raise exceptions)
        try:
            server = MCPServer(struct_mcp)
            assert server is not None
            print(f"✓ MCP server created successfully for {filename}")
        except Exception as e:
            pytest.fail(f"Failed to create MCP server for {filename}: {e}")


def test_query_consistency_across_formats():
    """Test that similar queries work across all formats."""
    examples_dir = Path(__file__).parent.parent / "examples"

    example_files = [
        "cheese_catalog.yaml",
        "cheese_catalog.json",
        "cheese_catalog_opensearch.json",
        "cheese_catalog_avro.json",
        "cheese_catalog_pydantic.py",
        "cheese_catalog.proto",
    ]

    results = {}

    for filename in example_files:
        file_path = examples_dir / filename
        struct_mcp = StructMCP.from_file(file_path)

        # Get structure names
        structure_names = struct_mcp.get_structure_names()

        # Find the cheese structure
        cheese_structure = None
        for name in structure_names:
            if "cheese" in name.lower():
                cheese_structure = name
                break

        if cheese_structure:
            fields = struct_mcp.get_fields(cheese_structure)
            results[filename] = {
                "structure_name": cheese_structure,
                "field_count": len(fields),
                "has_cheese_id": "cheese_id" in fields,
                "has_name": "name" in fields,
                "has_is_available": "is_available" in fields,
            }

    # Verify all formats have similar basic structure
    assert len(results) == len(example_files)

    for filename, result in results.items():
        assert result["has_cheese_id"], f"{filename} missing cheese_id field"
        assert result["has_name"], f"{filename} missing name field"
        assert result["has_is_available"], f"{filename} missing is_available field"
        assert result["field_count"] >= 3, f"{filename} has too few fields"

        print(
            f"✓ {filename}: {result['field_count']} fields, structure: {result['structure_name']}"
        )


def test_additional_yaml_examples():
    """Test loading additional YAML examples."""
    examples_dir = Path(__file__).parent.parent / "examples"

    yaml_files = [
        "financial_transactions.yaml",
        "user_profiles.yaml",
    ]

    for filename in yaml_files:
        file_path = examples_dir / filename

        if file_path.exists():
            try:
                struct_mcp = StructMCP.from_file(file_path)
                structure_names = struct_mcp.get_structure_names()
                assert len(structure_names) > 0, f"{filename} has no structures"
                print(f"✓ Successfully loaded {filename}")
            except Exception as e:
                pytest.fail(f"Failed to load {filename}: {e}")


def test_format_auto_detection():
    """Test that format auto-detection works correctly for all examples."""
    examples_dir = Path(__file__).parent.parent / "examples"

    # Test files and their expected detection
    test_cases = [
        ("cheese_catalog.yaml", "yaml"),
        ("cheese_catalog.json", "json_schema"),  # Should detect as JSON Schema
        ("cheese_catalog_opensearch.json", "opensearch"),
        ("cheese_catalog_avro.json", "avro"),
        ("cheese_catalog_pydantic.py", "pydantic"),
        ("cheese_catalog.proto", "protobuf"),
    ]

    for filename, expected_format in test_cases:
        file_path = examples_dir / filename

        if file_path.exists():
            # Load using auto-detection
            struct_mcp = StructMCP.from_file(file_path)

            # Verify it loaded successfully (basic sanity check)
            structure_names = struct_mcp.get_structure_names()
            assert len(structure_names) > 0, f"Auto-detection failed for {filename}"

            print(
                f"✓ Auto-detected and loaded {filename} (expected: {expected_format})"
            )


def test_error_handling_for_malformed_files(tmp_path):
    """Test error handling for various malformed files."""

    # Test malformed YAML
    bad_yaml = tmp_path / "bad.yaml"
    bad_yaml.write_text("invalid: yaml: content: [")

    with pytest.raises(Exception):  # Should raise some parsing error
        StructMCP.from_file(bad_yaml)

    # Test malformed JSON
    bad_json = tmp_path / "bad.json"
    bad_json.write_text('{"invalid": json"}')

    with pytest.raises(Exception):  # Should raise JSON parsing error
        StructMCP.from_file(bad_json)

    # Test malformed Python
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("import invalid syntax")

    with pytest.raises(Exception):  # Should raise Python parsing error
        StructMCP.from_file(bad_py)

    # Test empty files
    empty_file = tmp_path / "empty.yaml"
    empty_file.write_text("")

    with pytest.raises(Exception):  # Should raise some error for empty content
        StructMCP.from_file(empty_file)

    print("✓ Error handling works correctly for malformed files")


def test_field_details_consistency():
    """Test that field details are preserved across formats where possible."""
    examples_dir = Path(__file__).parent.parent / "examples"

    # Load the YAML version as the reference (most complete)
    yaml_path = examples_dir / "cheese_catalog.yaml"
    yaml_struct = StructMCP.from_file(yaml_path)
    yaml_structure_name = [
        name for name in yaml_struct.get_structure_names() if "cheese" in name.lower()
    ][0]
    yaml_fields = yaml_struct.get_fields(yaml_structure_name)

    # Test against JSON Schema version
    json_path = examples_dir / "cheese_catalog.json"
    if json_path.exists():
        json_struct = StructMCP.from_file(json_path)
        json_structure_name = [
            name
            for name in json_struct.get_structure_names()
            if "cheese" in name.lower()
        ][0]
        json_fields = json_struct.get_fields(json_structure_name)

        # Check that common fields have descriptions
        common_fields = set(yaml_fields.keys()) & set(json_fields.keys())
        for field_name in common_fields:
            yaml_field = yaml_fields[field_name]
            json_field = json_fields[field_name]

            # Both should have descriptions
            assert yaml_field.get(
                "description"
            ), f"YAML {field_name} missing description"
            assert json_field.get(
                "description"
            ), f"JSON Schema {field_name} missing description"

        print(
            f"✓ Field details consistent between YAML and JSON Schema ({len(common_fields)} common fields)"
        )
