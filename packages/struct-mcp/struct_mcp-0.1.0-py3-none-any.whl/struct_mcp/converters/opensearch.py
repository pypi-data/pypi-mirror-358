"""
OpenSearch mapping converter.
"""

import json
from typing import Any, Dict


class OpenSearchConverter:
    """Convert structure definitions to OpenSearch mapping format."""

    def convert(self, structures: Dict[str, Any]) -> str:
        """Convert structures to OpenSearch mapping JSON."""
        mappings = {}

        for structure_name, structure_data in structures.items():
            if isinstance(structure_data, dict) and "fields" in structure_data:
                mapping = self._convert_structure(structure_data["fields"])
                mappings[structure_name] = {"mappings": {"properties": mapping}}

        return json.dumps(mappings, indent=2)

    def _convert_structure(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Convert field definitions to OpenSearch property mappings."""
        properties = {}

        for field_name, field_data in fields.items():
            if isinstance(field_data, dict):
                prop = self._convert_field(field_data)
                properties[field_name] = prop
            else:
                # Simple field definition
                properties[field_name] = {"type": "text"}

        return properties

    def _convert_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single field to OpenSearch property."""
        prop = {}

        # Map common types
        field_type = field_data.get("type", "text")
        type_mapping = {
            "string": "text",
            "integer": "integer",
            "boolean": "boolean",
            "decimal": "double",
            "float": "float",
            "date": "date",
            "datetime": "date",
        }

        prop["type"] = type_mapping.get(field_type, "text")

        # Add keyword subfield for text fields to support exact matching
        if prop["type"] == "text":
            prop["fields"] = {"keyword": {"type": "keyword", "ignore_above": 256}}

        return prop
