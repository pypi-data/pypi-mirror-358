"""
JSON Schema parser for structure definitions.
"""

import json
from pathlib import Path
from typing import Any, Dict, Union


class JSONSchemaParser:
    """Parser for JSON Schema structure definition files."""

    def parse(self, schema_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse a JSON Schema structure definition file."""
        schema_path = Path(schema_path)

        if not schema_path.exists():
            raise FileNotFoundError(f"JSON Schema file not found: {schema_path}")

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError(
                    "JSON Schema file must contain a dictionary at the root level"
                )

            # Convert JSON Schema format to our internal format
            return self._convert_json_schema(data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing JSON Schema file: {e}")

    def _convert_json_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON Schema format to our internal structure format."""
        result = {}

        # Handle root-level schema with properties
        if "properties" in schema:
            structure_name = schema.get("title", schema.get("$id", "structure"))
            if structure_name.startswith("#") or structure_name.startswith("http"):
                # Extract meaningful name from URI or use default
                structure_name = "structure"
            result[structure_name] = self._convert_schema_object(schema)

        # Handle definitions/components that define multiple structures
        elif "$defs" in schema or "definitions" in schema:
            defs = schema.get("$defs", schema.get("definitions", {}))
            for name, definition in defs.items():
                result[name] = self._convert_schema_object(definition)

        # Handle oneOf/anyOf patterns that might define multiple structures
        elif "oneOf" in schema or "anyOf" in schema:
            schemas = schema.get("oneOf", schema.get("anyOf", []))
            for i, sub_schema in enumerate(schemas):
                if isinstance(sub_schema, dict):
                    name = sub_schema.get("title", f"structure_{i}")
                    result[name] = self._convert_schema_object(sub_schema)

        # Handle direct structure definitions
        else:
            # Try to extract structure name from title, $id, or use filename
            structure_name = schema.get("title", schema.get("$id", "structure"))
            if structure_name.startswith("#") or structure_name.startswith("http"):
                structure_name = "structure"
            result[structure_name] = self._convert_schema_object(schema)

        return result

    def _convert_schema_object(self, schema_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single JSON Schema object to our internal format."""
        result = {}

        # Extract metadata
        if "description" in schema_obj:
            result["description"] = schema_obj["description"]
        else:
            result["description"] = "Structure imported from JSON Schema"

        # Extract version if present
        if "version" in schema_obj:
            result["version"] = schema_obj["version"]

        # Extract custom properties for business context
        for key in [
            "business_owner",
            "upstream_table",
            "calculation_logic",
            "business_rules",
        ]:
            if key in schema_obj:
                result[key] = schema_obj[key]

        # Convert properties to fields
        if "properties" in schema_obj:
            result["fields"] = {}
            properties = schema_obj["properties"]
            required_fields = set(schema_obj.get("required", []))

            for field_name, field_schema in properties.items():
                result["fields"][field_name] = self._convert_field_schema(
                    field_schema, nullable=field_name not in required_fields
                )
        else:
            result["fields"] = {}

        return result

    def _convert_field_schema(
        self, field_schema: Dict[str, Any], nullable: bool = True
    ) -> Dict[str, Any]:
        """Convert a JSON Schema field definition to our internal format."""
        result = {}

        # Handle type conversion
        json_type = field_schema.get("type")

        if json_type == "string":
            result["type"] = "string"
        elif json_type == "integer":
            result["type"] = "integer"
        elif json_type == "number":
            result["type"] = "decimal"
        elif json_type == "boolean":
            result["type"] = "boolean"
        elif json_type == "array":
            # Handle array type
            items_schema = field_schema.get("items", {})
            if isinstance(items_schema, dict):
                item_type = items_schema.get("type", "string")
                result["type"] = self._map_json_type(item_type)
            else:
                result["type"] = "string"
            result["repeated"] = True
        elif json_type == "object":
            # Treat objects as strings for now (could be expanded to nested structures)
            result["type"] = "string"
        elif isinstance(json_type, list):
            # Union types - find the first non-null type
            non_null_types = [t for t in json_type if t != "null"]
            if "null" in json_type:
                nullable = True

            if non_null_types:
                result["type"] = self._map_json_type(non_null_types[0])
            else:
                result["type"] = "string"
        else:
            result["type"] = "string"  # Default fallback

        # Set nullability
        result["nullable"] = nullable

        # Handle repeated fields (arrays)
        if "repeated" not in result:
            result["repeated"] = False

        # Extract description
        if "description" in field_schema:
            result["description"] = field_schema["description"]
        else:
            result["description"] = (
                f"Field of type {json_type} imported from JSON Schema"
            )

        # Extract custom business context properties
        for key in ["upstream_table", "calculation_logic", "business_rules"]:
            if key in field_schema:
                result[key] = field_schema[key]

        # Handle enum values as part of description
        if "enum" in field_schema:
            enum_values = field_schema["enum"]
            result[
                "description"
            ] += f" (allowed values: {', '.join(map(str, enum_values))})"

        # Handle format constraints
        if "format" in field_schema:
            format_type = field_schema["format"]
            if format_type in ["date", "date-time"]:
                result["type"] = "string"  # Keep as string but note the format
                result["description"] += f" (format: {format_type})"

        return result

    def _map_json_type(self, json_type: str) -> str:
        """Map JSON Schema types to our internal types."""
        type_mapping = {
            "string": "string",
            "integer": "integer",
            "number": "decimal",
            "boolean": "boolean",
            "object": "string",
            "array": "string",
        }
        return type_mapping.get(json_type, "string")

    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of parsed JSON Schema data."""
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
