from pathlib import Path
import yaml
from pydantic_settings import BaseSettings
from pydantic import ValidationError


class AzureConfig(BaseSettings):
    storage_account: str
    container_name: str
    connection_string: str


def load_config(config_model, config_path: Path):
    """
    Loads configuration from a YAML file and validates it with a Pydantic model.
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)

    try:
        return config_model(**config_data.get("azure", {}))
    except (ValidationError, TypeError) as e:
        raise ValueError(f"Azure configuration validation error in {config_path}: {e}") from e