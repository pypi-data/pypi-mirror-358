"""
Tests for URI parsing functionality in MCP server.
"""

import pytest
from struct_mcp.mcp_server import extract_structure_name_from_uri


class TestExtractStructureNameFromUri:
    """Test cases for extract_structure_name_from_uri function."""

    def test_struct_scheme_netloc(self):
        """Test extraction from struct:// scheme using netloc."""
        uri = "struct://cheese_inventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_https_scheme_path(self):
        """Test extraction from HTTPS URL using path."""
        uri = "https://example.com/api/cheese_inventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_file_scheme_path(self):
        """Test extraction from file:// URL using path."""
        uri = "file:///path/to/cheese_inventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_http_scheme_multiple_path_segments(self):
        """Test extraction from HTTP URL with multiple path segments."""
        uri = "http://api.example.com/v1/structures/cheese_inventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_custom_scheme_netloc(self):
        """Test extraction from custom scheme using netloc."""
        uri = "myscheme://user_profile"
        result = extract_structure_name_from_uri(uri)
        assert result == "user_profile"

    def test_ftp_scheme_path(self):
        """Test extraction from FTP URL using path."""
        uri = "ftp://server.com/data/product_catalog"
        result = extract_structure_name_from_uri(uri)
        assert result == "product_catalog"

    def test_path_with_trailing_slash(self):
        """Test extraction when path has trailing slash."""
        uri = "https://example.com/api/cheese_inventory/"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_path_with_multiple_trailing_slashes(self):
        """Test extraction when path has multiple trailing slashes."""
        uri = "https://example.com/api/cheese_inventory///"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_nested_path_structure(self):
        """Test extraction from deeply nested path."""
        uri = "https://api.company.com/v2/data/catalogs/food/cheese_inventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_uri_with_query_parameters(self):
        """Test extraction ignores query parameters."""
        uri = "https://example.com/api/cheese_inventory?format=json&version=1"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_uri_with_fragment(self):
        """Test extraction ignores URL fragments."""
        uri = "https://example.com/api/cheese_inventory#section1"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_uri_with_port_number(self):
        """Test extraction works with port numbers in netloc."""
        uri = "https://example.com:8080/api/cheese_inventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory"

    def test_special_characters_in_structure_name(self):
        """Test extraction with special characters in structure name."""
        uri = "struct://cheese-inventory_v2"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese-inventory_v2"

    def test_numeric_structure_name(self):
        """Test extraction with numeric structure name."""
        uri = "struct://structure123"
        result = extract_structure_name_from_uri(uri)
        assert result == "structure123"

    def test_empty_uri_raises_error(self):
        """Test that empty URI raises ValueError."""
        with pytest.raises(ValueError, match="Cannot extract structure name from URI"):
            extract_structure_name_from_uri("")

    def test_uri_with_only_scheme_raises_error(self):
        """Test that URI with only scheme raises ValueError."""
        with pytest.raises(ValueError, match="Cannot extract structure name from URI"):
            extract_structure_name_from_uri("https://")

    def test_uri_with_empty_path_and_netloc_raises_error(self):
        """Test that URI with empty path and netloc raises ValueError."""
        with pytest.raises(ValueError, match="Cannot extract structure name from URI"):
            extract_structure_name_from_uri("scheme:")

    def test_uri_with_only_slashes_falls_back_to_netloc(self):
        """Test that URI with only slashes falls back to netloc."""
        uri = "https://example.com///"
        result = extract_structure_name_from_uri(uri)
        assert result == "example.com"

    def test_root_path_only_falls_back_to_netloc(self):
        """Test that URI with only root path falls back to netloc."""
        uri = "https://example.com/"
        result = extract_structure_name_from_uri(uri)
        assert result == "example.com"

    def test_anyurl_object_conversion(self):
        """Test that function works with objects that convert to string."""

        class MockAnyUrl:
            def __str__(self):
                return "struct://mock_structure"

        mock_uri = MockAnyUrl()
        result = extract_structure_name_from_uri(mock_uri)
        assert result == "mock_structure"

    def test_none_input_converts_to_string(self):
        """Test that None input gets converted to string 'None'."""
        result = extract_structure_name_from_uri(None)
        assert result == "None"

    def test_unicode_structure_name(self):
        """Test extraction with Unicode characters in structure name."""
        uri = "struct://测试结构"
        result = extract_structure_name_from_uri(uri)
        assert result == "测试结构"

    def test_case_sensitivity_preserved(self):
        """Test that case is preserved in structure name."""
        uri = "struct://CheeseInventory"
        result = extract_structure_name_from_uri(uri)
        assert result == "CheeseInventory"

    def test_file_extension_preserved(self):
        """Test that file extensions are preserved if present."""
        uri = "file:///data/structures/cheese_inventory.json"
        result = extract_structure_name_from_uri(uri)
        assert result == "cheese_inventory.json"
