"""
Tests for Pydantic model parser.
"""

import pytest
from pathlib import Path
from struct_mcp.parsers.pydantic_parser import PydanticParser


def test_pydantic_parser_valid_model(tmp_path):
    """Test parsing a valid Pydantic model file."""
    model_content = '''
from typing import List, Optional
from pydantic import BaseModel, Field


class CheeseInventory(BaseModel):
    """Artisanal cheese catalog with provenance tracking"""
    
    cheese_id: str = Field(description="Unique identifier for each cheese")
    name: str = Field(description="Display name of the cheese")
    stinkiness_level: Optional[int] = Field(description="Stinkiness rating from 1-10")
    emoji: str = Field(description="Visual representation for UI")
    origin_country: Optional[str] = Field(description="Country of origin")
    tasting_notes: Optional[List[str]] = Field(description="Expert tasting descriptions")
    is_available: bool = Field(description="Currently in stock and available for purchase")
    price_per_pound: Optional[float] = Field(description="Current retail price per pound in USD")


class SupplierInfo(BaseModel):
    """Supplier information"""
    
    supplier_id: str
    supplier_name: str
    contact_email: Optional[str] = None
'''

    model_file = tmp_path / "test_model.py"
    model_file.write_text(model_content)

    parser = PydanticParser()
    result = parser.parse(model_file)

    assert "cheese_inventory" in result
    assert "supplier_info" in result
    assert "fields" in result["cheese_inventory"]
    assert "cheese_id" in result["cheese_inventory"]["fields"]

    # Check field properties
    cheese_id_field = result["cheese_inventory"]["fields"]["cheese_id"]
    assert cheese_id_field["type"] == "string"
    assert cheese_id_field["nullable"] == False
    assert cheese_id_field["repeated"] == False
    assert "Unique identifier" in cheese_id_field["description"]

    # Check optional field
    stinkiness_field = result["cheese_inventory"]["fields"]["stinkiness_level"]
    assert stinkiness_field["type"] == "integer"
    assert stinkiness_field["nullable"] == True

    # Check list field
    tasting_notes_field = result["cheese_inventory"]["fields"]["tasting_notes"]
    assert tasting_notes_field["type"] == "string"
    assert tasting_notes_field["repeated"] == True
    assert tasting_notes_field["nullable"] == True

    # Check docstring extraction
    assert "Artisanal cheese catalog" in result["cheese_inventory"]["description"]


def test_pydantic_parser_simple_types(tmp_path):
    """Test parsing Pydantic model with simple types."""
    model_content = """
from pydantic import BaseModel

class SimpleModel(BaseModel):
    string_field: str
    int_field: int
    bool_field: bool
    float_field: float
    optional_field: str = None
"""

    model_file = tmp_path / "simple_model.py"
    model_file.write_text(model_content)

    parser = PydanticParser()
    result = parser.parse(model_file)

    assert "simple_model" in result
    fields = result["simple_model"]["fields"]

    assert fields["string_field"]["type"] == "string"
    assert fields["int_field"]["type"] == "integer"
    assert fields["bool_field"]["type"] == "boolean"
    assert fields["float_field"]["type"] == "decimal"
    assert fields["optional_field"]["nullable"] == True


def test_pydantic_parser_no_basemodel(tmp_path):
    """Test parsing file with no BaseModel classes."""
    model_content = """
class RegularClass:
    def __init__(self):
        self.field = "value"

def some_function():
    return "hello"
"""

    model_file = tmp_path / "no_basemodel.py"
    model_file.write_text(model_content)

    parser = PydanticParser()
    result = parser.parse(model_file)

    assert result == {}  # No BaseModel classes found


def test_pydantic_parser_nonexistent_file():
    """Test parsing a non-existent file."""
    parser = PydanticParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.py")


def test_pydantic_parser_invalid_python(tmp_path):
    """Test parsing invalid Python syntax."""
    invalid_content = """
class InvalidModel(BaseModel):
    field: str = "unclosed string
    another_field: int
"""

    model_file = tmp_path / "invalid.py"
    model_file.write_text(invalid_content)

    parser = PydanticParser()

    with pytest.raises(ValueError):
        parser.parse(model_file)


def test_pydantic_parser_inheritance_detection(tmp_path):
    """Test detection of BaseModel inheritance."""
    model_content = """
from pydantic import BaseModel
from some_module import SomeBase

class DirectInheritance(BaseModel):
    field1: str

class IndirectInheritance(SomeBase):
    field2: str

from pydantic import BaseModel as BM

class AliasedInheritance(BM):
    field3: str
"""

    model_file = tmp_path / "inheritance_test.py"
    model_file.write_text(model_content)

    parser = PydanticParser()
    result = parser.parse(model_file)

    # Should only detect DirectInheritance and AliasedInheritance
    assert "direct_inheritance" in result
    assert "aliased_inheritance" in result
    assert "indirect_inheritance" not in result


def test_pydantic_parser_class_name_conversion():
    """Test conversion of class names to structure names."""
    parser = PydanticParser()

    assert parser._to_structure_name("CheeseInventory") == "cheese_inventory"
    assert parser._to_structure_name("SimpleModel") == "simple_model"
    assert parser._to_structure_name("XMLHttpRequest") == "xmlhttp_request"
    assert parser._to_structure_name("IODevice") == "iodevice"
    assert parser._to_structure_name("lowercase") == "lowercase"


def test_pydantic_parser_complex_annotations(tmp_path):
    """Test parsing complex type annotations."""
    model_content = """
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ComplexModel(BaseModel):
    simple_list: List[str]
    optional_list: Optional[List[int]]
    nested_optional: Optional[str]
    any_field: Any
    dict_field: Dict[str, Any]
"""

    model_file = tmp_path / "complex_model.py"
    model_file.write_text(model_content)

    parser = PydanticParser()
    result = parser.parse(model_file)

    fields = result["complex_model"]["fields"]

    # Simple list
    assert fields["simple_list"]["type"] == "string"
    assert fields["simple_list"]["repeated"] == True
    assert fields["simple_list"]["nullable"] == False

    # Optional list
    assert fields["optional_list"]["type"] == "integer"
    assert fields["optional_list"]["repeated"] == True
    assert fields["optional_list"]["nullable"] == True

    # Nested optional
    assert fields["nested_optional"]["type"] == "string"
    assert fields["nested_optional"]["nullable"] == True
    assert fields["nested_optional"]["repeated"] == False


def test_pydantic_parser_validation():
    """Test validation method."""
    parser = PydanticParser()

    # Valid data
    valid_data = {"structure1": {"fields": {"field1": {"type": "string"}}}}
    assert parser.validate(valid_data) == True

    # Invalid data
    assert parser.validate("not a dict") == False
    assert parser.validate({}) == True  # Empty is valid
