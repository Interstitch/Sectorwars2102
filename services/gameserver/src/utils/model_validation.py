"""
Model validation utilities to prevent field name mismatches and attribute errors.
Part of self-improving development strategy.
"""

from typing import Any, List, Optional, Type, Dict
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect


class ModelFieldValidator:
    """Utility class to validate model field access and prevent common errors."""
    
    @staticmethod
    def get_model_fields(model_class: Type[DeclarativeBase]) -> List[str]:
        """Get all field names for a SQLAlchemy model."""
        inspector = inspect(model_class)
        return [column.name for column in inspector.columns]
    
    @staticmethod
    def get_model_relationships(model_class: Type[DeclarativeBase]) -> List[str]:
        """Get all relationship names for a SQLAlchemy model."""
        inspector = inspect(model_class)
        return [rel.key for rel in inspector.relationships]
    
    @staticmethod
    def validate_field_exists(model_class: Type[DeclarativeBase], field_name: str) -> bool:
        """Check if a field exists on a model."""
        fields = ModelFieldValidator.get_model_fields(model_class)
        relationships = ModelFieldValidator.get_model_relationships(model_class)
        return field_name in fields or field_name in relationships
    
    @staticmethod
    def safe_get_enum_value(obj: Any, field_name: str, default: str = "UNKNOWN") -> str:
        """
        Safely get enum value from an object attribute.
        Handles None values and missing attributes.
        """
        if not hasattr(obj, field_name):
            return default
        
        field_value = getattr(obj, field_name)
        if field_value is None:
            return default
        
        # If it's an enum, get the value
        if hasattr(field_value, 'value'):
            return field_value.value
        
        # Otherwise return as string
        return str(field_value)
    
    @staticmethod
    def safe_check_attribute(obj: Any, attr_name: str) -> bool:
        """
        Safely check if an object has an attribute and it's not None.
        Returns False if attribute doesn't exist or is None.
        """
        return hasattr(obj, attr_name) and getattr(obj, attr_name) is not None
    
    @staticmethod
    def get_model_info(model_class: Type[DeclarativeBase]) -> Dict[str, Any]:
        """Get comprehensive information about a model for debugging."""
        return {
            "table_name": model_class.__tablename__,
            "fields": ModelFieldValidator.get_model_fields(model_class),
            "relationships": ModelFieldValidator.get_model_relationships(model_class),
            "primary_keys": [col.name for col in inspect(model_class).primary_key]
        }


def validate_sector_query_fields():
    """
    Validate that Sector model has the fields we expect in our queries.
    This prevents the errors we just fixed.
    """
    from src.models.sector import Sector
    
    # Fields we commonly access in admin routes
    expected_fields = [
        'id', 'sector_id', 'name', 'type', 'cluster_id',
        'x_coord', 'y_coord', 'z_coord', 'hazard_level',
        'is_discovered', 'controlling_faction'
    ]
    
    # Optional fields that might be None
    optional_fields = ['special_type']
    
    missing_fields = []
    model_fields = ModelFieldValidator.get_model_fields(Sector)
    
    for field in expected_fields:
        if not ModelFieldValidator.validate_field_exists(Sector, field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Sector model missing expected fields: {missing_fields}")
    
    return {
        "status": "valid",
        "expected_fields": expected_fields,
        "optional_fields": optional_fields,
        "all_fields": model_fields
    }


def validate_port_query_fields():
    """Validate Port model fields for admin queries."""
    from src.models.port import Port
    
    expected_fields = [
        'id', 'name', 'sector_id', 'sector_uuid', 'owner_id',
        'port_class', 'type', 'status'
    ]
    
    missing_fields = []
    for field in expected_fields:
        if not ModelFieldValidator.validate_field_exists(Port, field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Port model missing expected fields: {missing_fields}")
    
    return {"status": "valid", "expected_fields": expected_fields}


def validate_planet_query_fields():
    """Validate Planet model fields for admin queries."""
    from src.models.planet import Planet
    
    expected_fields = [
        'id', 'name', 'sector_id', 'sector_uuid', 'owner_id',
        'type', 'status'
    ]
    
    missing_fields = []
    for field in expected_fields:
        if not ModelFieldValidator.validate_field_exists(Planet, field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Planet model missing expected fields: {missing_fields}")
    
    return {"status": "valid", "expected_fields": expected_fields}


def validate_warp_tunnel_query_fields():
    """Validate WarpTunnel model fields for admin queries."""
    from src.models.warp_tunnel import WarpTunnel
    
    expected_fields = [
        'id', 'origin_sector_id', 'destination_sector_id',
        'type', 'status', 'is_bidirectional', 'stability'
    ]
    
    missing_fields = []
    for field in expected_fields:
        if not ModelFieldValidator.validate_field_exists(WarpTunnel, field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"WarpTunnel model missing expected fields: {missing_fields}")
    
    return {"status": "valid", "expected_fields": expected_fields}


def run_all_model_validations() -> Dict[str, Any]:
    """Run all model field validations and return results."""
    results = {}
    
    validations = [
        ("Sector", validate_sector_query_fields),
        ("Port", validate_port_query_fields), 
        ("Planet", validate_planet_query_fields),
        ("WarpTunnel", validate_warp_tunnel_query_fields)
    ]
    
    for model_name, validation_func in validations:
        try:
            results[model_name] = validation_func()
        except Exception as e:
            results[model_name] = {"status": "error", "error": str(e)}
    
    return results


if __name__ == "__main__":
    # Allow running validation directly
    import sys
    sys.path.append('/app')
    
    print("🔍 Running Model Field Validations")
    print("=" * 40)
    
    results = run_all_model_validations()
    
    all_valid = True
    for model_name, result in results.items():
        if result["status"] == "valid":
            print(f"✅ {model_name}: All expected fields present")
        else:
            print(f"❌ {model_name}: {result.get('error', 'Validation failed')}")
            all_valid = False
    
    if all_valid:
        print("\n🎉 All model validations passed!")
    else:
        print("\n❌ Some validations failed. Check model definitions.")
    
    print("\n💡 Use these utilities in your code to prevent field name errors.")