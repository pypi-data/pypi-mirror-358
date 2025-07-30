import os
import orjson
import yaml
from dotenv import dotenv_values


def parse_config(config_path: str) -> dict:
    """Parse a config file based on its extension."""
    ext = os.path.splitext(config_path)[1].lower()

    if ext == ".json":
        with open(config_path, "rb") as f:
            return orjson.loads(f.read())
    elif ext in (".yaml", ".yml"):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    elif ext in ('.env', ''):
        return dotenv_values(config_path)
    else:
        raise ValueError(f"Unsupported config format: {ext}")
