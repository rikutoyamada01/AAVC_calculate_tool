from datetime import date
from unittest.mock import patch

import pytest

from src.AAVC_calculate_tool.algorithm_registry import AlgorithmRegistry
from src.AAVC_calculate_tool.backtester import ComparisonResult, run_comparison_backtest
from src.AAVC_calculate_tool.calculator import (
    AAVCStaticStrategy,
    AAVCDynamicStrategy,
    AAVCMovingAverageStrategy,
    BuyAndHoldStrategy,
    DCAStrategy,
)

# Mock the ALGORITHM_REGISTRY for consistent testing
@pytest.fixture(autouse=True)
def mock_algorithm_registry():
    registry = AlgorithmRegistry()
    registry.register(AAVCStaticStrategy)
    registry.register(AAVCDynamicStrategy)
    registry.register(AAVCMovingAverageStrategy)
    registry.register(DCAStrategy)
    registry.register(BuyAndHoldStrategy)
    with patch('src.AAVC_calculate_tool.backtester.ALGORITHM_REGISTRY', registry):
        yield registry


# Mock data_loader.fetch_price_history_by_date
@pytest.fixture
def mock_price_history():
    with patch('src.AAVC_calculate_tool.backtester.fetch_price_history_by_date') as mock_fetch:
        mock_fetch.return_value = (
            [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0],
            [date(2023, 1, i + 1).isoformat() for i in range(10)]
        )
        yield mock_fetch


class TestInvestmentStrategies:
    """Test cases for individual investment strategy classes."""

    def test_aavc_static_strategy_calculate_investment(self):
        strategy = AAVCStaticStrategy()
        price_history = [100.0, 101.0, 102.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {"base_amount": 10000.0, "ref_price": 100.0,
                  "asymmetric_coefficient": 2.0, "investment_frequency": "daily"}
        investment = strategy.calculate_investment(
            current_price=102.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert investment < 10000.0
        assert investment >= 0.0

class TestMultiAlgorithmBacktest:
    """Test cases for the multi-algorithm backtest functionality."""

    def test_run_comparison_backtest_default_algorithms(self, mock_price_history):
        result = run_comparison_backtest(
            ticker="TEST",
            start_date_str="2023-01-01",
            end_date_str="2023-01-10",
            base_parameters={'base_amount': 10000.0}
        )

        assert isinstance(result, ComparisonResult)
        assert "aavc_static" in result.results
        assert "aavc_dynamic" in result.results
        assert "aavc_ma" in result.results
        assert "dca" in result.results
        assert "buy_and_hold" in result.results
        assert len(result.results) == 5

    def test_run_comparison_backtest_specific_algorithms(self, mock_price_history):
        result = run_comparison_backtest(
            ticker="TEST",
            start_date_str="2023-01-01",
            end_date_str="2023-01-10",
            base_parameters={'base_amount': 10000.0},
            algorithm_names=["aavc_static", "dca"]
        )

        assert isinstance(result, ComparisonResult)
        assert "aavc_static" in result.results
        assert "dca" in result.results
        assert "buy_and_hold" not in result.results
        assert len(result.results) == 2

    def test_run_comparison_backtest_with_algo_params(self, mock_price_history):
        mock_price_history.return_value = (
            [100.0, 99.0, 98.0, 97.0, 96.0, 95.0, 94.0, 93.0, 92.0, 91.0],
            [date(2023, 1, i + 1).isoformat() for i in range(10)]
        )

        result = run_comparison_backtest(
            ticker="TEST",
            start_date_str="2023-01-01",
            end_date_str="2023-01-10",
            base_parameters={
                'base_amount': 10000.0,
                'aavc_static': {'ref_price': 95.0, 'asymmetric_coefficient': 3.0}
            },
            algorithm_names=["aavc_static"]
        )

        assert isinstance(result, ComparisonResult)
        assert "aavc_static" in result.results
        aavc_result = result.results["aavc_static"]
        assert aavc_result.metadata['ref_price'] == 95.0
        assert aavc_result.metadata['asymmetric_coefficient'] == 3.0

    def test_run_comparison_backtest_no_price_data(self):
        with patch('src.AAVC_calculate_tool.backtester.fetch_price_history_by_date') as mock_fetch:
            mock_fetch.return_value = ([], [])
            with pytest.raises(ValueError, match="No price data available for the specified period."):
                run_comparison_backtest(
                    ticker="TEST",
                    start_date_str="2023-01-01",
                    end_date_str="2023-01-10",
                    base_parameters={'base_amount': 10000.0}
                )
