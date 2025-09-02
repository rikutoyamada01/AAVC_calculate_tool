
import pytest

from src.AAVC_calculate_tool.config_loader import (
    ConfigNotFoundError,
    ConfigParseError,
    load_config,
    prepare_calculation_jobs,
    _load_and_validate_calculation_config, # Added this import
)


# Helper function to create a temporary config file
def create_temp_config_file(tmp_path, filename, content):
    file_path = tmp_path / filename
    file_path.write_text(content)
    return file_path


# --- Fixtures for config content ---
@pytest.fixture
def valid_config_content():
    return """
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 2.0
stocks:
  - ticker: AAPL
    reference_price: 150.0
  - ticker: GOOGL
    base_amount: 5000
    reference_price: 2800.0
"""


@pytest.fixture
def malformed_yaml_content():
    return """
default_settings:
  base_amount: 10000
stocks:
- ticker: AAPL
  - this is not valid yaml
"""


@pytest.fixture
def missing_default_settings_content():
    return """
stocks:
  - ticker: AAPL
"""


@pytest.fixture
def missing_stocks_content():
    return """
default_settings:
  base_amount: 10000
"""


@pytest.fixture
def not_a_dict_content():
    return """
- item1
- item2
"""


# --- Test load_config function ---

def test_load_config_valid_file(tmp_path, valid_config_content):
    config_file = create_temp_config_file(tmp_path, "valid_config.yaml",
                                          valid_config_content)
    config = load_config(str(config_file))
    assert isinstance(config, dict)
    assert config["default_settings"]["base_amount"] == 10000
    assert len(config["stocks"]) == 2


def test_load_config_file_not_found(tmp_path):
    with pytest.raises(ConfigNotFoundError) as excinfo:
        load_config(str(tmp_path / "non_existent.yaml"))
    assert "Config file not found" in str(excinfo.value)


def test_load_config_malformed_yaml(tmp_path, malformed_yaml_content):
    config_file = create_temp_config_file(tmp_path, "malformed.yaml",
                                          malformed_yaml_content)
    with pytest.raises(ConfigParseError) as excinfo:
        load_config(str(config_file))
    assert "Error parsing YAML configuration file" in str(excinfo.value)


def test_load_config_missing_default_settings(tmp_path,
                                              missing_default_settings_content):
    config_file = create_temp_config_file(tmp_path, "missing_default.yaml",
                                          missing_default_settings_content)
    with pytest.raises(ConfigParseError) as excinfo:
        _load_and_validate_calculation_config(str(config_file))
    assert "'default_settings' section is missing or malformed." in str(excinfo.value)


def test_load_config_missing_stocks(tmp_path, missing_stocks_content):
    config_file = create_temp_config_file(tmp_path, "missing_stocks.yaml",
                                          missing_stocks_content)
    with pytest.raises(ConfigParseError) as excinfo:
        _load_and_validate_calculation_config(str(config_file))
    assert "'stocks' section is missing or malformed." in str(excinfo.value)


def test_load_config_not_a_dict(tmp_path, not_a_dict_content):
    config_file = create_temp_config_file(tmp_path, "not_a_dict.yaml",
                                          not_a_dict_content)
    with pytest.raises(ConfigParseError) as excinfo:
        load_config(str(config_file))
    assert "Invalid config file format: Root must be a dictionary." in str(excinfo.value)


# --- Test prepare_calculation_jobs function ---

def test_prepare_calculation_jobs_basic(tmp_path, valid_config_content):
    config_file = create_temp_config_file(tmp_path, "valid_config.yaml",
                                          valid_config_content)
    config = load_config(str(config_file))
    jobs = prepare_calculation_jobs(config)

    assert len(jobs) == 2
    assert jobs[0]["ticker"] == "AAPL"
    assert jobs[0]["base_amount"] == 10000  # From default_settings
    assert jobs[0]["reference_price"] == 150.0
    assert jobs[0]["asymmetric_coefficient"] == 2.0  # From default_settings

    assert jobs[1]["ticker"] == "GOOGL"
    assert jobs[1]["base_amount"] == 5000  # Overridden in stock config
    assert jobs[1]["reference_price"] == 2800.0
    assert jobs[1]["asymmetric_coefficient"] == 2.0  # From default_settings


def test_prepare_calculation_jobs_no_override(tmp_path, valid_config_content):
    # Modify config to remove overrides for GOOGL
    content = valid_config_content.replace(
        "    base_amount: 5000\n    reference_price: 2800.0\n", ""
    )
    config_file = create_temp_config_file(tmp_path, "no_override.yaml", content)
    config = load_config(str(config_file))
    jobs = prepare_calculation_jobs(config)

    assert jobs[1]["ticker"] == "GOOGL"
    assert jobs[1]["base_amount"] == 10000  # Should now be from default_settings
    assert jobs[1]["reference_price"] is None  # No override, no default for ref_price
    assert jobs[1]["asymmetric_coefficient"] == 2.0
