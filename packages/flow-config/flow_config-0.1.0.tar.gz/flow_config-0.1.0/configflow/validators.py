from pydantic import ValidationError, create_model
from typing import Dict, Type


def validate_config(config: dict, schema: Dict[str, Type]) -> dict:
    """Validate a config dictionary against a schema."""
    # Create a dynamic pydantic model with fields from the schema
    fields = {key: (type_, ...) for key, type_ in schema.items()}
    ConfigModel = create_model("ConfigModel", **fields)

    try:
        model = ConfigModel(**config)
        return model.model_dump()
    except ValidationError as e:
        raise ValueError(f"Config validation failed: {e}") from e
