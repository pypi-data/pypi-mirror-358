"""
Tests for YAML parser.
"""

import pytest
from pathlib import Path
from struct_mcp.parsers.yaml_parser import YAMLParser


def test_yaml_parser_valid_file(tmp_path):
    """Test parsing a valid YAML file."""
    yaml_content = """
cheese_inventory:
  description: "Artisanal cheese catalog"
  fields:
    cheese_id:
      type: string
      nullable: false
      description: "Unique identifier"
    name:
      type: string
      nullable: false
      description: "Cheese name"
"""

    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml_content)

    parser = YAMLParser()
    result = parser.parse(yaml_file)

    assert "cheese_inventory" in result
    assert "fields" in result["cheese_inventory"]
    assert "cheese_id" in result["cheese_inventory"]["fields"]


def test_yaml_parser_nonexistent_file():
    """Test parsing a non-existent file."""
    parser = YAMLParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.yaml")


def test_yaml_parser_invalid_yaml(tmp_path):
    """Test parsing invalid YAML."""
    yaml_content = """
invalid: yaml: content:
  - missing
    - bracket
"""

    yaml_file = tmp_path / "invalid.yaml"
    yaml_file.write_text(yaml_content)

    parser = YAMLParser()

    with pytest.raises(ValueError):
        parser.parse(yaml_file)
