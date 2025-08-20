import sys
from unittest.mock import MagicMock, patch

import pytest

from AAVC_calculate_tool.backtester import ComparisonResult, EnhancedBacktestResult
from AAVC_calculate_tool.config_loader import ConfigNotFoundError
from AAVC_calculate_tool.data_loader import TickerNotFoundError


# Mock the external dependencies
@pytest.fixture
def mock_dependencies():
    with patch(
        'AAVC_calculate_tool.__main__.fetch_price_history') as mock_fetch_price_history, \
        patch('AAVC_calculate_tool.__main__.load_config') as mock_load_config, \
        patch('AAVC_calculate_tool.__main__.prepare_calculation_jobs') as \
            mock_prepare_calculation_jobs, \
        patch('AAVC_calculate_tool.__main__.run_comparison_backtest') as \
            mock_run_comparison_backtest, \
        patch('AAVC_calculate_tool.__main__.generate_dynamic_summary_table') as \
            mock_generate_summary_table, \
        patch('AAVC_calculate_tool.__main__.plot_multi_algorithm_chart') as mock_plot_chart:

        # Configure mocks for successful single ticker calc
        mock_fetch_price_history.return_value = [
            100.0, 101.0, 102.0]  # Dummy price history

        # Configure mocks for config file mode
        mock_load_config.return_value = {
            "default_settings": {"base_amount": 10000, "asymmetric_coefficient": 2.0},
            "stocks": [
                {"ticker": "AAPL", "reference_price": 150.0},
                {"ticker": "GOOGL", "base_amount": 5000, "reference_price": 2800.0}
            ]
        }
        mock_prepare_calculation_jobs.return_value = [
            {"ticker": "AAPL", "base_amount": 10000, "reference_price": 150.0,
             "asymmetric_coefficient": 2.0},
            {"ticker": "GOOGL", "base_amount": 5000, "reference_price": 2800.0,
             "asymmetric_coefficient": 2.0}
        ]

        # Configure mock for run_comparison_backtest
        mock_comparison_result = MagicMock(spec=ComparisonResult)
        mock_comparison_result.results = {
            "aavc": MagicMock(spec=EnhancedBacktestResult, final_value=12000.0,
                              total_invested=10000.0, portfolio_history=[100, 200],
                              investment_history=[10000.0]),
            "dca": MagicMock(spec=EnhancedBacktestResult, final_value=11000.0,
                             total_invested=9000.0, portfolio_history=[100, 200],
                             investment_history=[9000.0]),
        }
        mock_comparison_result.summary = {"best_performer": "aavc"}
        mock_comparison_result.rankings = {"total_return": ["aavc", "dca"]}
        mock_comparison_result.correlations = {"aavc": {"dca": 0.5}}
        mock_run_comparison_backtest.return_value = mock_comparison_result

        mock_generate_summary_table.return_value = "Mock Summary Table"
        mock_plot_chart.return_value = "mock_chart.png"

        yield {
            "fetch_price_history": mock_fetch_price_history,
            "load_config": mock_load_config,
            "prepare_calculation_jobs": mock_prepare_calculation_jobs,
            "run_comparison_backtest": mock_run_comparison_backtest,
            "generate_dynamic_summary_table": mock_generate_summary_table,
            "plot_multi_algorithm_chart": mock_plot_chart,
        }


# Helper to capture stdout
@pytest.fixture
def capsys_stdout(capsys):
    # This fixture is built-in to pytest, just renaming for clarity
    return capsys


# --- Test 'calc' subcommand - Single Ticker Mode ---


def test_calc_single_ticker_success(mock_dependencies, capsys_stdout):
    sys.argv = ["__main__.py", "calc", "--ticker", "TEST", "--amount", "10000"]
    from AAVC_calculate_tool.__main__ import main
    main()

    mock_dependencies["fetch_price_history"].assert_called_with("TEST")
    # AAVCStrategy.calculate_investment is called internally, not mocked directly here

    captured = capsys_stdout.readouterr()
    assert "Calculation Result" in captured.out
    assert "Ticker: TEST" in captured.out
    # The exact amount depends on AAVCStrategy logic, not a fixed mock value
    assert "Investment Amount: JPY" in captured.out


def test_calc_single_ticker_missing_amount(capsys_stdout):
    sys.argv = ["__main__.py", "calc", "--ticker", "TEST"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1

    captured = capsys_stdout.readouterr()
    assert "Error: --amount is required when --ticker is specified." in captured.out


def test_calc_single_ticker_invalid_ticker(mock_dependencies, capsys_stdout):
    mock_dependencies["fetch_price_history"].side_effect = TickerNotFoundError(
        "Test Ticker Not Found")

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
    main()

    mock_dependencies["load_config"].assert_called_once_with("test_config.yaml")
    mock_dependencies["prepare_calculation_jobs"].assert_called_once()
    assert mock_dependencies["fetch_price_history"].call_count == 2

    captured = capsys_stdout.readouterr()
    assert "Ticker: AAPL" in captured.out
    assert "Ticker: GOOGL" in captured.out
    assert "Investment Amount: JPY" in captured.out


def test_calc_config_file_not_found(mock_dependencies, capsys_stdout):
    mock_dependencies["load_config"].side_effect = ConfigNotFoundError(
        "Config file not found")

    sys.argv = ["__main__.py", "calc", "--config", "non_existent.yaml"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1

    captured = capsys_stdout.readouterr()
    assert "Error: Config file not found" in captured.out


# --- Test 'backtest' subcommand ---


def test_backtest_default_algorithms(mock_dependencies, capsys_stdout):
    sys.argv = ["__main__.py", "backtest", "--ticker", "TEST",
                "--start-date", "2023-01-01", "--end-date", "2023-01-10",
                "--amount", "10000"]
    from AAVC_calculate_tool.__main__ import main
    main()

    mock_dependencies["run_comparison_backtest"].assert_called_once_with(
        ticker="TEST",
        start_date_str="2023-01-01",
        end_date_str="2023-01-10",
        base_parameters={'base_amount': 10000.0},
        algorithm_names=None
    )
    mock_dependencies["generate_dynamic_summary_table"].assert_called_once()
    mock_dependencies["plot_multi_algorithm_chart"].assert_not_called()

    captured = capsys_stdout.readouterr()
    assert "Mock Summary Table" in captured.out


def test_backtest_specific_algorithms(mock_dependencies, capsys_stdout):
    sys.argv = ["__main__.py", "backtest", "--ticker", "TEST",
                "--start-date", "2023-01-01", "--end-date", "2023-01-10",
                "--amount", "10000", "--algorithms", "aavc,dca"]
    from AAVC_calculate_tool.__main__ import main
    main()

    mock_dependencies["run_comparison_backtest"].assert_called_once_with(
        ticker="TEST",
        start_date_str="2023-01-01",
        end_date_str="2023-01-10",
        base_parameters={'base_amount': 10000.0},
        algorithm_names=["aavc", "dca"]
    )


def test_backtest_with_algorithm_params(mock_dependencies, capsys_stdout):
    sys.argv = ["__main__.py", "backtest", "--ticker", "TEST",
                "--start-date", "2023-01-01", "--end-date", "2023-01-10",
                "--amount", "10000",
                "--algorithms", "aavc",
                "--algorithm-params",
                "aavc:reference_price=150.0;asymmetric_coefficient=2.5"]
    from AAVC_calculate_tool.__main__ import main
    main()

    mock_dependencies["run_comparison_backtest"].assert_called_once_with(
        ticker="TEST",
        start_date_str="2023-01-01",
        end_date_str="2023-01-10",
        base_parameters={'base_amount': 10000.0,
                         'aavc': {'reference_price': 150.0,
                                  'asymmetric_coefficient': 2.5}},
        algorithm_names=["aavc"]
    )


def test_backtest_plot_generation(mock_dependencies, capsys_stdout):
    sys.argv = ["__main__.py", "backtest", "--ticker", "TEST",
                "--start-date", "2023-01-01", "--end-date", "2023-01-10",
                "--amount", "10000", "--plot"]
    from AAVC_calculate_tool.__main__ import main
    main()

    mock_dependencies["plot_multi_algorithm_chart"].assert_called_once()
    captured = capsys_stdout.readouterr()
    assert "Chart saved to:" in captured.out


def test_backtest_invalid_ticker_error(mock_dependencies, capsys_stdout):
    mock_dependencies["run_comparison_backtest"].side_effect = TickerNotFoundError(
        "Invalid Ticker")

    sys.argv = ["__main__.py", "backtest", "--ticker", "INVALID",
                "--start-date", "2023-01-01", "--end-date", "2023-01-10",
                "--amount", "10000"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1
    captured = capsys_stdout.readouterr()
    assert "Error: Invalid Ticker" in captured.out


def test_backtest_invalid_algorithm_error(mock_dependencies, capsys_stdout):
    mock_dependencies["run_comparison_backtest"].side_effect = ValueError(
        "Algorithm 'unknown' not found")

    sys.argv = ["__main__.py", "backtest", "--ticker", "TEST",
                "--start-date", "2023-01-01", "--end-date", "2023-01-10",
                "--amount", "10000", "--algorithms", "unknown"]
    from AAVC_calculate_tool.__main__ import main
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()

    assert pytest_wrapped_e.type is SystemExit
    assert pytest_wrapped_e.value.code == 1
    captured = capsys_stdout.readouterr()
    assert "Error: Algorithm 'unknown' not found" in captured.out
