from pathlib import Path
from typing import List, Optional, TypedDict

import yaml


# Custom exceptions (as per detailed design)
class ConfigError(Exception):
    pass

class ConfigNotFoundError(ConfigError):
    pass

class ConfigParseError(ConfigError):
    pass

# Type definitions for config structure
class StockConfig(TypedDict):
    ticker: str
    reference_price: Optional[float] # Made optional as per CLI design
    base_amount: Optional[float]
    asymmetric_coefficient: Optional[float]

class DefaultSettings(TypedDict):
    base_amount: float
    asymmetric_coefficient: float

class AppConfig(TypedDict):
    default_settings: DefaultSettings
    stocks: List[StockConfig]

def load_config(file_path: str) -> AppConfig:
    """
    YAML設定ファイルを読み込み、型定義に沿った辞書として返す。
    """
    config_path = Path(file_path)
    if not config_path.exists():
        raise ConfigNotFoundError(f"Configuration file not found at '{file_path}'")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigParseError(f"Error parsing YAML configuration file '{file_path}': {e}") from e
    except Exception as e:
        raise ConfigError(f"An unexpected error occurred while loading config file '{file_path}': {e}") from e

    # Basic validation (more detailed validation can be added later)
    if not isinstance(config_data, dict):
        raise ConfigParseError("Invalid config file format: Root must be a dictionary.")
    if "default_settings" not in config_data or not isinstance(config_data["default_settings"], dict):
        raise ConfigParseError("Invalid config file format: 'default_settings' section is missing or malformed.")
    if "stocks" not in config_data or not isinstance(config_data["stocks"], list):
        raise ConfigParseError("Invalid config file format: 'stocks' section is missing or malformed.")

    # Type casting (runtime check, mypy handles static check)
    return config_data # type: ignore

def prepare_calculation_jobs(config: AppConfig) -> List[dict]:
    """
    AppConfigオブジェクトから、計算に必要なパラメータのリストを準備する。
    default_settingsを各銘柄の設定にマージする。
    """
    jobs = []
    default_base_amount = config['default_settings'].get('base_amount', 0.0)
    default_asymmetric_coefficient = config['default_settings'].get('asymmetric_coefficient', 2.0)

    for stock_config in config['stocks']:
        job_params = {
            "ticker": stock_config["ticker"],
            "base_amount": stock_config.get("base_amount", default_base_amount),
            "reference_price": stock_config.get("reference_price"), # Can be None, handled by calc logic
            "asymmetric_coefficient": stock_config.get("asymmetric_coefficient", default_asymmetric_coefficient)
        }
        jobs.append(job_params)
    return jobs
