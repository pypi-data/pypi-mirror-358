"""JSON Schema to Pydantic model conversion utilities"""

from pydantic import BaseModel, create_model
from typing import Dict, Any, Optional, List


def json_schema_to_pydantic(schema: Dict[str, Any], class_name: str) -> BaseModel:
    """Convert JSON Schema to Pydantic model dynamically"""
    
    properties = schema.get("properties", {})
    required_fields = set(schema.get("required", []))
    
    field_definitions = {}
    
    for field_name, field_schema in properties.items():
        field_type = _get_python_type(field_schema)
        default_value = field_schema.get("default", ...)
        
        if field_name not in required_fields and default_value == ...:
            field_type = Optional[field_type]
            default_value = None
            
        field_definitions[field_name] = (field_type, default_value)
    
    return create_model(class_name, **field_definitions)


def _get_python_type(field_schema: Dict[str, Any]):
    """Convert JSON Schema type to Python type"""
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": List[Any],
        "object": Dict[str, Any]
    }
    
    json_type = field_schema.get("type", "string")
    return type_mapping.get(json_type, str) 