"""
Converter for generating Protocol Buffer (.proto) schemas from structure definitions.
"""

from typing import Any, Dict


class ProtobufConverter:
    """Convert structure definitions to Protocol Buffer schema format."""

    def convert(self, structures: Dict[str, Any]) -> str:
        """Convert structures to Protocol Buffer schema format."""
        lines = ['syntax = "proto3";', "", "package generated_schema;", ""]

        for structure_name, structure_data in structures.items():
            if not isinstance(structure_data, dict):
                continue

            lines.extend(self._convert_structure(structure_name, structure_data))
            lines.append("")

        return "\n".join(lines)

    def _convert_structure(self, name: str, data: Dict[str, Any]) -> list:
        """Convert a single structure to Protocol Buffer message format."""
        lines = []

        # Add description as comment if available
        if "description" in data:
            lines.append(f'// {data["description"]}')

        # Convert structure name to PascalCase for proto message naming
        message_name = self._to_pascal_case(name)
        lines.append(f"message {message_name} {{")

        # Convert fields
        if "fields" in data and isinstance(data["fields"], dict):
            field_number = 1
            for field_name, field_data in data["fields"].items():
                field_lines = self._convert_field(field_name, field_data, field_number)
                lines.extend([f"    {line}" for line in field_lines])
                field_number += 1

        lines.append("}")

        return lines

    def _convert_field(
        self, name: str, data: Dict[str, Any], field_number: int
    ) -> list:
        """Convert a field to Protocol Buffer field format."""
        lines = []

        if not isinstance(data, dict):
            # Simple field without metadata
            lines.append(f"string {name} = {field_number};")
            return lines

        # Add description as comment
        if "description" in data:
            lines.append(f'// {data["description"]}')

        # Determine field modifiers
        modifiers = []
        if data.get("repeated", False):
            modifiers.append("repeated")
        elif data.get("nullable", False):
            modifiers.append("optional")

        # Convert type
        proto_type = self._map_type_to_proto(data.get("type", "string"))

        # Build field definition
        modifier_str = " ".join(modifiers) + " " if modifiers else ""
        lines.append(f"{modifier_str}{proto_type} {name} = {field_number};")

        return lines

    def _map_type_to_proto(self, internal_type: str) -> str:
        """Map internal types to Protocol Buffer types."""
        type_mapping = {
            "string": "string",
            "integer": "int32",
            "decimal": "double",
            "boolean": "bool",
        }

        return type_mapping.get(internal_type, "string")

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase."""
        components = snake_str.split("_")
        return "".join(word.capitalize() for word in components)
