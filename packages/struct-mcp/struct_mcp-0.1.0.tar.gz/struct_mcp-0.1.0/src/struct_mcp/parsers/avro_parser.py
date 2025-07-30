"""
Avro schema parser for structure definitions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union


class AvroParser:
    """Parser for Avro schema files."""

    def parse(self, schema_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse an Avro schema file."""
        schema_path = Path(schema_path)

        if not schema_path.exists():
            raise FileNotFoundError(f"Avro schema file not found: {schema_path}")

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert Avro format to our internal format
            return self._convert_avro_schema(data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing Avro schema file: {e}")

    def _convert_avro_schema(
        self, schema: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Convert Avro schema format to our internal structure format."""
        result = {}

        # Handle array of schemas
        if isinstance(schema, list):
            for schema_item in schema:
                if (
                    isinstance(schema_item, dict)
                    and schema_item.get("type") == "record"
                ):
                    structure_name = schema_item.get("name", "structure")
                    result[structure_name] = self._convert_record_schema(schema_item)

        # Handle single schema
        elif isinstance(schema, dict):
            if schema.get("type") == "record":
                structure_name = schema.get("name", "structure")
                result[structure_name] = self._convert_record_schema(schema)
            else:
                raise ValueError("Avro schema must be a record type at the root level")

        else:
            raise ValueError("Invalid Avro schema format")

        return result

    def _convert_record_schema(self, record_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert an Avro record schema to our internal format."""
        result = {}

        # Extract metadata
        if "doc" in record_schema:
            result["description"] = record_schema["doc"]
        else:
            result["description"] = (
                f"Structure imported from Avro schema: {record_schema.get('name', 'unknown')}"
            )

        # Convert fields
        result["fields"] = {}
        if "fields" in record_schema:
            for field_schema in record_schema["fields"]:
                field_name = field_schema.get("name")
                if field_name:
                    result["fields"][field_name] = self._convert_field_schema(
                        field_schema
                    )

        return result

    def _convert_field_schema(self, field_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert an Avro field schema to our internal format."""
        result = {}

        # Extract field type information
        field_type = field_schema.get("type")
        type_info = self._parse_avro_type(field_type)

        result["type"] = type_info["base_type"]
        result["nullable"] = type_info["nullable"]
        result["repeated"] = type_info["repeated"]

        # Extract description
        if "doc" in field_schema:
            result["description"] = field_schema["doc"]
        else:
            result["description"] = (
                f"Field of type {field_type} imported from Avro schema"
            )

        # Extract any custom properties that might be in the schema
        for key in ["upstream_table", "calculation_logic", "business_rules"]:
            if key in field_schema:
                result[key] = field_schema[key]

        return result

    def _parse_avro_type(
        self, avro_type: Union[str, Dict[str, Any], List[Any]]
    ) -> Dict[str, Any]:
        """Parse Avro type definition and return type information."""
        result = {"base_type": "string", "nullable": False, "repeated": False}

        # Handle simple string types
        if isinstance(avro_type, str):
            result["base_type"] = self._map_avro_type(avro_type)

        # Handle union types (typically for nullable fields)
        elif isinstance(avro_type, list):
            # Union type - check for null and extract base type
            non_null_types = [t for t in avro_type if t != "null"]
            if "null" in avro_type:
                result["nullable"] = True

            if non_null_types:
                # Take the first non-null type
                base_type = non_null_types[0]
                if isinstance(base_type, dict) and base_type.get("type") == "array":
                    result["repeated"] = True
                    item_type = base_type.get("items", "string")
                    result["base_type"] = self._map_avro_type(item_type)
                else:
                    result["base_type"] = self._map_avro_type(base_type)

        # Handle complex types (arrays, records, etc.)
        elif isinstance(avro_type, dict):
            type_name = avro_type.get("type")

            if type_name == "array":
                result["repeated"] = True
                item_type = avro_type.get("items", "string")
                result["base_type"] = self._map_avro_type(item_type)
            elif type_name == "record":
                result["base_type"] = (
                    "string"  # Treat nested records as strings for now
                )
            else:
                result["base_type"] = self._map_avro_type(type_name)

        return result

    def _map_avro_type(self, avro_type: Union[str, Any]) -> str:
        """Map Avro types to our internal types."""
        if not isinstance(avro_type, str):
            return "string"

        type_mapping = {
            "string": "string",
            "int": "integer",
            "long": "integer",
            "float": "decimal",
            "double": "decimal",
            "boolean": "boolean",
            "bytes": "string",
            "null": "string",
        }

        return type_mapping.get(avro_type, "string")

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of parsed Avro schema data."""
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
