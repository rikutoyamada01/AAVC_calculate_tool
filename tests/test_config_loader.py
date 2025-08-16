from pathlib import Path

import pytest

from src.AAVC_calculate_tool.config_loader import (
    ConfigNotFoundError,
    ConfigParseError,
    load_config,
    prepare_calculation_jobs,
)

# --- Fixtures for test config files ---

@pytest.fixture
def valid_config_content():
    return """
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 2.0

stocks:
  - ticker: "AAPL"
    reference_price: 150.0
  - ticker: "GOOGL"
    base_amount: 5000
    reference_price: 2800.0
  - ticker: "SPY"
"""

@pytest.fixture
def malformed_yaml_content():
    return """
default_settings:
  base_amount: 10000
stocks:
  - ticker: "AAPL"
    invalid_key: : # Malformed YAML
"""

@pytest.fixture
def missing_default_settings_content():
    return """
stocks:
  - ticker: "AAPL"
"""

@pytest.fixture
def missing_stocks_content():
    return """
default_settings:
  base_amount: 10000
"""

@pytest.fixture
def empty_config_content():
    return ""

# --- Helper to create a temporary config file ---
def create_temp_config_file(tmp_path: Path, filename: str, content: str) -> Path:
    file_path = tmp_path / filename
    file_path.write_text(content)
    return file_path

# --- Test load_config function ---

def test_load_config_valid_file(tmp_path, valid_config_content):
    config_file = create_temp_config_file(tmp_path, "valid_config.yaml", valid_config_content)
    config = load_config(str(config_file))
    assert isinstance(config, dict)
    assert "default_settings" in config
    assert "stocks" in config
    assert len(config["stocks"]) == 3
    assert config["stocks"][0]["ticker"] == "AAPL"

def test_load_config_non_existent_file(tmp_path):
    with pytest.raises(ConfigNotFoundError) as excinfo:
        load_config(str(tmp_path / "non_existent.yaml"))
    assert "Configuration file not found" in str(excinfo.value)

def test_load_config_malformed_yaml(tmp_path, malformed_yaml_content):
    config_file = create_temp_config_file(tmp_path, "malformed.yaml", malformed_yaml_content)
    with pytest.raises(ConfigParseError) as excinfo:
        load_config(str(config_file))
    assert "Error parsing YAML configuration file" in str(excinfo.value)

def test_load_config_missing_default_settings(tmp_path, missing_default_settings_content):
    config_file = create_temp_config_file(tmp_path, "missing_default.yaml", missing_default_settings_content)
    with pytest.raises(ConfigParseError) as excinfo:
        load_config(str(config_file))
    assert "'default_settings' section is missing or malformed" in str(excinfo.value)

def test_load_config_missing_stocks(tmp_path, missing_stocks_content):
    config_file = create_temp_config_file(tmp_path, "missing_stocks.yaml", missing_stocks_content)
    with pytest.raises(ConfigParseError) as excinfo:
        load_config(str(config_file))
    assert "'stocks' section is missing or malformed" in str(excinfo.value)

def test_load_config_empty_file(tmp_path, empty_config_content):
    config_file = create_temp_config_file(tmp_path, "empty.yaml", empty_config_content)
    with pytest.raises(ConfigParseError) as excinfo:
        load_config(str(config_file))
    assert "Invalid config file format: Root must be a dictionary." in str(excinfo.value)

# --- Test prepare_calculation_jobs function ---

def test_prepare_calculation_jobs_basic(tmp_path, valid_config_content):
    config_file = create_temp_config_file(tmp_path, "valid_config.yaml", valid_config_content)
    config = load_config(str(config_file))
    jobs = prepare_calculation_jobs(config)

    assert len(jobs) == 3
    assert jobs[0]["ticker"] == "AAPL"
    assert jobs[0]["base_amount"] == 10000 # Default from config
    assert jobs[0]["reference_price"] == 150.0
    assert jobs[0]["asymmetric_coefficient"] == 2.0 # Default from config

    assert jobs[1]["ticker"] == "GOOGL"
    assert jobs[1]["base_amount"] == 5000 # Overridden
    assert jobs[1]["reference_price"] == 2800.0
    assert jobs[1]["asymmetric_coefficient"] == 2.0 # Default

    assert jobs[2]["ticker"] == "SPY"
    assert jobs[2]["base_amount"] == 10000 # Default
    assert jobs[2]["reference_price"] is None # Not specified, so None
    assert jobs[2]["asymmetric_coefficient"] == 2.0 # Default

def test_prepare_calculation_jobs_with_overrides(tmp_path):
    content = """
default_settings:
  base_amount: 1000
  asymmetric_coefficient: 1.5

stocks:
  - ticker: "TEST1"
  - ticker: "TEST2"
    base_amount: 2000
    asymmetric_coefficient: 3.0
    reference_price: 50.0
"""
    config_file = create_temp_config_file(tmp_path, "override_config.yaml", content)
    config = load_config(str(config_file))
    jobs = prepare_calculation_jobs(config)

    assert len(jobs) == 2
    assert jobs[0]["ticker"] == "TEST1"
    assert jobs[0]["base_amount"] == 1000
    assert jobs[0]["asymmetric_coefficient"] == 1.5
    assert jobs[0]["reference_price"] is None

    assert jobs[1]["ticker"] == "TEST2"
    assert jobs[1]["base_amount"] == 2000
    assert jobs[1]["asymmetric_coefficient"] == 3.0
    assert jobs[1]["reference_price"] == 50.0
