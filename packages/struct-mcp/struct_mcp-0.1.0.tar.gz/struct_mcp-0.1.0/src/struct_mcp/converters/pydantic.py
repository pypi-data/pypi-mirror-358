"""
Pydantic model converter.
"""

from typing import Any, Dict


class PydanticConverter:
    """Convert structure definitions to Pydantic model format."""

    def convert(self, structures: Dict[str, Any]) -> str:
        """Convert structures to Pydantic model Python code."""
        lines = []

        # Imports
        lines.append("from typing import List, Optional")
        lines.append("from pydantic import BaseModel, Field")
        lines.append("")

        # Generate model for each structure
        for structure_name, structure_data in structures.items():
            if isinstance(structure_data, dict) and "fields" in structure_data:
                model_code = self._convert_structure(structure_name, structure_data)
                lines.extend(model_code)
                lines.append("")

        return "\n".join(lines)

    def _convert_structure(
        self, structure_name: str, structure_data: Dict[str, Any]
    ) -> list[str]:
        """Convert structure to Pydantic model class."""
        lines = []

        # Class definition
        class_name = self._to_class_name(structure_name)
        lines.append(f"class {class_name}(BaseModel):")

        # Docstring
        description = structure_data.get("description")
        if description:
            lines.append(f'    """{description}"""')
            lines.append("")

        # Fields
        fields_data = structure_data["fields"]
        if not fields_data:
            lines.append("    pass")
        else:
            for field_name, field_data in fields_data.items():
                field_lines = self._convert_field(field_name, field_data)
                lines.extend(field_lines)

        return lines

    def _convert_field(self, field_name: str, field_data: Any) -> list[str]:
        """Convert a single field to Pydantic field definition."""
        lines = []

        if not isinstance(field_data, dict):
            # Simple field
            lines.append(f"    {field_name}: str")
            return lines

        # Get type information
        field_type = field_data.get("type", "string")
        nullable = field_data.get("nullable", False)
        repeated = field_data.get("repeated", False)
        description = field_data.get("description")

        # Map types
        type_mapping = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "decimal": "float",
            "float": "float",
            "date": "str",
            "datetime": "str",
        }

        python_type = type_mapping.get(field_type, "str")

        # Handle repeated (List) types
        if repeated:
            python_type = f"List[{python_type}]"

        # Handle nullable (Optional) types
        if nullable:
            python_type = f"Optional[{python_type}]"
            default_value = " = None"
        else:
            default_value = ""

        # Build field definition
        field_def = f"    {field_name}: {python_type}"

        # Add Field() with description if present
        if description:
            field_def += f' = Field(description="{description}")'
        else:
            field_def += default_value

        lines.append(field_def)

        return lines

    def _to_class_name(self, structure_name: str) -> str:
        """Convert structure name to Python class name."""
        # Convert snake_case to PascalCase
        parts = structure_name.replace("-", "_").split("_")
        return "".join(word.capitalize() for word in parts)
