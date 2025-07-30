"""
OpenSearch mapping parser for structure definitions.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union


class OpenSearchParser:
    """Parser for OpenSearch mapping files."""

    def parse(self, mapping_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse an OpenSearch mapping file."""
        mapping_path = Path(mapping_path)

        if not mapping_path.exists():
            raise FileNotFoundError(
                f"OpenSearch mapping file not found: {mapping_path}"
            )

        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError(
                    "OpenSearch mapping file must contain a dictionary at the root level"
                )

            # Convert OpenSearch format to our internal format
            return self._convert_opensearch_mapping(data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing OpenSearch mapping file: {e}")

    def _convert_opensearch_mapping(self, mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenSearch mapping format to our internal structure format."""
        result = {}

        # Handle different OpenSearch mapping structures
        for structure_name, structure_data in mapping.items():
            if isinstance(structure_data, dict):
                # Handle nested mappings structure
                if "mappings" in structure_data:
                    mappings = structure_data["mappings"]
                    if "properties" in mappings:
                        result[structure_name] = self._convert_properties(
                            mappings["properties"]
                        )
                    else:
                        result[structure_name] = self._convert_properties(mappings)
                # Handle direct properties
                elif "properties" in structure_data:
                    result[structure_name] = self._convert_properties(
                        structure_data["properties"]
                    )
                # Handle if the structure_data itself contains field mappings
                else:
                    result[structure_name] = self._convert_properties(structure_data)

        return result

    def _convert_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenSearch properties to our internal format."""
        result = {
            "description": "Structure imported from OpenSearch mapping",
            "fields": {},
        }

        for field_name, field_mapping in properties.items():
            if isinstance(field_mapping, dict):
                result["fields"][field_name] = self._convert_field_mapping(
                    field_mapping
                )
            else:
                # Simple field definition
                result["fields"][field_name] = {
                    "type": "string",
                    "nullable": True,
                    "repeated": False,
                    "description": f"Field imported from OpenSearch mapping",
                }

        return result

    def _convert_field_mapping(self, field_mapping: Dict[str, Any]) -> Dict[str, Any]:
        """Convert OpenSearch field mapping to our internal format."""
        result = {}

        # Map OpenSearch types to our types
        opensearch_type = field_mapping.get("type", "text")
        type_mapping = {
            "text": "string",
            "keyword": "string",
            "integer": "integer",
            "long": "integer",
            "short": "integer",
            "byte": "integer",
            "double": "decimal",
            "float": "decimal",
            "boolean": "boolean",
            "date": "string",  # Store as string for now
            "binary": "string",
            "object": "string",
            "nested": "string",
        }

        result["type"] = type_mapping.get(opensearch_type, "string")

        # OpenSearch fields can generally be null unless explicitly configured
        result["nullable"] = True

        # Check if this is an array field (not directly supported in OpenSearch mappings)
        result["repeated"] = False

        # Add description if available
        if "description" in field_mapping:
            result["description"] = field_mapping["description"]
        else:
            result["description"] = (
                f"Field of type {opensearch_type} imported from OpenSearch mapping"
            )

        # Extract any custom properties that might be in the mapping
        for key in ["upstream_table", "calculation_logic", "business_rules"]:
            if key in field_mapping:
                result[key] = field_mapping[key]

        return result

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of parsed OpenSearch mapping data."""
        if not isinstance(data, dict):
            return False

        # Check that each top-level item has some structure
        for structure_name, structure_data in data.items():
            if not isinstance(structure_data, dict):
                continue

            # If it has fields, validate field structure
            if "fields" in structure_data:
                fields = structure_data["fields"]
                if not isinstance(fields, dict):
                    return False

        return True
