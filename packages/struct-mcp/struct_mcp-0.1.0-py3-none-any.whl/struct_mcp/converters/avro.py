"""
Avro schema converter.
"""

import json
from typing import Any, Dict, List, Union


class AvroConverter:
    """Convert structure definitions to Avro schema format."""

    def convert(self, structures: Dict[str, Any]) -> str:
        """Convert structures to Avro schema JSON."""
        schemas = []

        for structure_name, structure_data in structures.items():
            if isinstance(structure_data, dict) and "fields" in structure_data:
                schema = self._convert_structure(structure_name, structure_data)
                schemas.append(schema)

        # If only one schema, return it directly, otherwise return array
        if len(schemas) == 1:
            return json.dumps(schemas[0], indent=2)
        else:
            return json.dumps(schemas, indent=2)

    def _convert_structure(
        self, structure_name: str, structure_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert structure to Avro record schema."""
        schema = {"type": "record", "name": structure_name, "fields": []}

        # Add description if available
        if "description" in structure_data:
            schema["doc"] = structure_data["description"]

        # Convert fields
        fields_data = structure_data["fields"]
        for field_name, field_data in fields_data.items():
            field_schema = self._convert_field(field_name, field_data)
            schema["fields"].append(field_schema)

        return schema

    def _convert_field(self, field_name: str, field_data: Any) -> Dict[str, Any]:
        """Convert a single field to Avro field schema."""
        field_schema = {"name": field_name, "type": self._get_avro_type(field_data)}

        # Add description if available
        if isinstance(field_data, dict) and "description" in field_data:
            field_schema["doc"] = field_data["description"]

        return field_schema

    def _get_avro_type(self, field_data: Any) -> Union[str, Dict[str, Any], List[Any]]:
        """Get Avro type for field data."""
        if not isinstance(field_data, dict):
            return "string"  # Default type

        field_type = field_data.get("type", "string")
        nullable = field_data.get("nullable", False)
        repeated = field_data.get("repeated", False)

        # Map types
        type_mapping = {
            "string": "string",
            "integer": "int",
            "boolean": "boolean",
            "decimal": "double",
            "float": "float",
            "date": "string",  # Could be int (days since epoch)
            "datetime": "long",  # Milliseconds since epoch
        }

        avro_type = type_mapping.get(field_type, "string")

        # Handle repeated (array) types
        if repeated:
            avro_type = {"type": "array", "items": avro_type}

        # Handle nullable types
        if nullable:
            avro_type = ["null", avro_type]

        return avro_type
