from typing import Any, Dict, List

import yaml

def load_config(file_path: str) -> Dict[str, Any]:
    """Load configuration from a YAML file without specific validation."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise ConfigNotFoundError(f"Config file not found at '{file_path}'.") from e
    except yaml.YAMLError as e:
        raise ConfigParseError(f"Error parsing YAML configuration file '{file_path}': {e}") from e
    except Exception as e:
        raise ConfigError(f"An unexpected error occurred while loading config file '{file_path}': {e}") from e

    if not isinstance(config_data, dict):
        raise ConfigParseError("Invalid config file format: Root must be a dictionary.")
    return config_data


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigNotFoundError(ConfigError):
    """Exception raised when the configuration file is not found."""
    pass


class ConfigParseError(ConfigError):
    """Exception raised when there's an error parsing the configuration file."""
    pass


def _load_and_validate_calculation_config(file_path: str) -> Dict[str, Any]:
    """Load and validate configuration for calculation jobs from a YAML file."""
    config_data = load_config(file_path)

    # Basic validation (more detailed validation can be added later)
    if "default_settings" not in config_data or \
            not isinstance(config_data["default_settings"], dict):
        raise ConfigParseError("Invalid config file format: 'default_settings' "
                               "section is missing or malformed.")
    if "stocks" not in config_data or not isinstance(config_data["stocks"], list):
        raise ConfigParseError("Invalid config file format: 'stocks' section is "
                               "missing or malformed.")

    # Type casting (runtime check, mypy handles static check)
    return config_data


def prepare_calculation_jobs(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Prepare a list of calculation jobs from the loaded configuration."""
    jobs = []
    default_base_amount = config['default_settings'].get('base_amount', 0.0)
    default_asymmetric_coefficient = config['default_settings'].get(
        'asymmetric_coefficient', 2.0)

    for stock_config in config['stocks']:
        job_params = {
            "ticker": stock_config["ticker"],
            "base_amount": stock_config.get("base_amount", default_base_amount),
            "reference_price": stock_config.get("reference_price"),
            "asymmetric_coefficient": stock_config.get(
                "asymmetric_coefficient", default_asymmetric_coefficient)
        }
        jobs.append(job_params)
    return jobs
