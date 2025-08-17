import sys
from unittest.mock import patch

import pytest

from AAVC_calculate_tool.config_loader import (
    ConfigNotFoundError,
)
from AAVC_calculate_tool.data_loader import TickerNotFoundError

# Assuming __main__.py is the entry point for the CLI
# We need to import main directly to test its functions
# from AAVC_calculate_tool.__main__ import main # This is the main entry point function
# However, testing argparse directly is often easier by mocking sys.argv
# and then calling the main function.

# Mock the external dependencies
@pytest.fixture
def mock_dependencies():
    with patch('AAVC_calculate_tool.__main__.fetch_price_history') as mock_fetch_price_history, \
         patch('AAVC_calculate_tool.__main__.calculate_aavc_investment') as mock_calculate_aavc_investment, \
         patch('AAVC_calculate_tool.__main__.load_config') as mock_load_config, \
         patch('AAVC_calculate_tool.__main__.prepare_calculation_jobs') as mock_prepare_calculation_jobs:

        # Configure mocks for successful single ticker calc
        mock_fetch_price_history.return_value = [100.0, 101.0, 102.0] # Dummy price history
        mock_calculate_aavc_investment.return_value = 12345.0 # Dummy calculated amount

        # Configure mocks for config file mode
        mock_load_config.return_value = {
            "default_settings": {"base_amount": 10000, "asymmetric_coefficient": 2.0},
            "stocks": [
                {"ticker": "AAPL", "reference_price": 150.0},
                {"ticker": "GOOGL", "base_amount": 5000, "reference_price": 2800.0}
            ]
        }
        mock_prepare_calculation_jobs.return_value = [
            {"ticker": "AAPL", "base_amount": 10000, "reference_price": 150.0, "asymmetric_coefficient": 2.0},
            {"ticker": "GOOGL", "base_amount": 5000, "reference_price": 2800.0, "asymmetric_coefficient": 2.0}
        ]

        yield {
            "fetch_price_history": mock_fetch_price_history,
            "calculate_aavc_investment": mock_calculate_aavc_investment,
            "load_config": mock_load_config,
            "prepare_calculation_jobs": mock_prepare_calculation_jobs
        }

# Helper to capture stdout
@pytest.fixture
def capsys_stdout(capsys):
    # This fixture is built-in to pytest, just renaming for clarity
    return capsys

# --- Test 'calc' subcommand - Single Ticker Mode ---

def test_calc_single_ticker_success(mock_dependencies, capsys_stdout):
    # Mock sys.argv to simulate command line arguments
    sys.argv = ["__main__.py", "calc", "--ticker", "TEST", "--amount", "10000"]

    # Import and run main function (which will parse sys.argv)
    from AAVC_calculate_tool.__main__ import main
    main() # No SystemExit expected for success

    # Check if mocks were called
    mock_dependencies["fetch_price_history"].assert_called_with("TEST")
    mock_dependencies["calculate_aavc_investment"].assert_called_once()

    # Check stdout output
    captured = capsys_stdout.readouterr()
    assert "Calculation Result" in captured.out
    assert "Ticker: TEST" in captured.out
    assert "Investment Amount: JPY 12345" in captured.out # From mock

def test_calc_single_ticker_missing_amount(capsys_stdout):
    sys.argv = ["__main__.py", "calc", "--ticker", "TEST"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1 # Expect error exit

    captured = capsys_stdout.readouterr()
    assert "Error: --amount is required when --ticker is specified." in captured.out

def test_calc_single_ticker_invalid_ticker(mock_dependencies, capsys_stdout):
    mock_dependencies["fetch_price_history"].side_effect = TickerNotFoundError("Test Ticker Not Found")

    sys.argv = ["__main__.py", "calc", "--ticker", "INVALID", "--amount", "10000"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1

    captured = capsys_stdout.readouterr()
    assert "Error: Test Ticker Not Found" in captured.out

# --- Test 'calc' subcommand - Config File Mode ---

def test_calc_config_file_success(mock_dependencies, capsys_stdout):
    sys.argv = ["__main__.py", "calc", "--config", "test_config.yaml"]
    from AAVC_calculate_tool.__main__ import main
    main() # No SystemExit expected for success

    # Check if mocks were called for each stock in config
    mock_dependencies["load_config"].assert_called_once_with("test_config.yaml")
    mock_dependencies["prepare_calculation_jobs"].assert_called_once()
    assert mock_dependencies["fetch_price_history"].call_count == 2 # For AAPL and GOOGL
    assert mock_dependencies["calculate_aavc_investment"].call_count == 2

    # Check stdout output for both stocks
    captured = capsys_stdout.readouterr()
    assert "Ticker: AAPL" in captured.out
    assert "Ticker: GOOGL" in captured.out
    assert "Investment Amount: JPY 12345" in captured.out # From mock

def test_calc_config_file_not_found(mock_dependencies, capsys_stdout):
    mock_dependencies["load_config"].side_effect = ConfigNotFoundError("Config file not found")

    sys.argv = ["__main__.py", "calc", "--config", "non_existent.yaml"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1

    captured = capsys_stdout.readouterr()
    assert "Error: Config file not found" in captured.out

# --- Test 'backtest' subcommand (placeholder) ---

def test_backtest_command_missing_required_args(capsys_stdout):
    sys.argv = ["__main__.py", "backtest", "--ticker", "TEST"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 2  # argparse error code

    captured = capsys_stdout.readouterr()
    assert "the following arguments are required" in captured.err
