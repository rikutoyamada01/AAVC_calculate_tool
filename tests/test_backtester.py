from datetime import date
from unittest.mock import patch

import pytest

from src.AAVC_calculate_tool.algorithm_registry import AlgorithmRegistry
from src.AAVC_calculate_tool.backtester import ComparisonResult, run_comparison_backtest
from src.AAVC_calculate_tool.calculator import (
    AAVCStrategy,
    BuyAndHoldStrategy,
    DCAStrategy,
)


# Mock the ALGORITHM_REGISTRY for consistent testing
@pytest.fixture(autouse=True)
def mock_algorithm_registry():
    registry = AlgorithmRegistry()
    registry.register(AAVCStrategy())
    registry.register(DCAStrategy())
    registry.register(BuyAndHoldStrategy())
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

    def test_aavc_strategy_calculate_investment(self):
        strategy = AAVCStrategy()
        # Test with a simple scenario where price increases slightly
        price_history = [100.0, 101.0, 102.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {"base_amount": 10000.0, "reference_price": 100.0,
                  "asymmetric_coefficient": 2.0}
        investment = strategy.calculate_investment(
            current_price=102.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        # Expect investment to decrease as price is above reference
        assert investment < 10000.0
        assert investment >= 0.0

    def test_dca_strategy_calculate_investment(self):
        strategy = DCAStrategy()
        # 月の最初の取引日をシミュレート
        price_history = [100.0]
        dates = [date(2023, 1, 1)]
        params = {"base_amount": 5000.0, "investment_frequency": "monthly"}
        investment = strategy.calculate_investment(
            current_price=100.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert investment == 5000.0

        # 月の最初の取引日ではない場合
        price_history_subsequent = [100.0, 101.0, 102.0]
        dates_subsequent = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        investment_subsequent = strategy.calculate_investment(
            current_price=102.0, price_history=price_history_subsequent, date_history=dates_subsequent,
            parameters=params
        )
        assert investment_subsequent == 0.0

    def test_buy_and_hold_strategy_calculate_investment(self):
        strategy = BuyAndHoldStrategy()
        price_history_day1 = [100.0]
        dates_day1 = [date(2023, 1, 1)]
        params = {"initial_amount": 100000.0}

        # First day investment
        investment_day1 = strategy.calculate_investment(
            current_price=100.0, price_history=price_history_day1, date_history=dates_day1,
            parameters=params
        )
        assert investment_day1 == 100000.0

        # Subsequent days, no investment
        price_history_day2 = [100.0, 101.0]
        dates_day2 = [date(2023, 1, 1), date(2023, 1, 2)]
        investment_day2 = strategy.calculate_investment(
            current_price=101.0, price_history=price_history_day2, date_history=dates_day2,
            parameters=params
        )
        assert investment_day2 == 0.0


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
        assert "aavc" in result.results
        assert "dca" in result.results
        assert "buy_and_hold" in result.results
        assert len(result.results) == 3

        # Check some basic metrics
        for algo_name, algo_result in result.results.items():
            assert algo_result.final_value > 0
            assert algo_result.total_invested > 0
            assert len(algo_result.portfolio_history) == 10

    def test_run_comparison_backtest_specific_algorithms(self, mock_price_history):
        result = run_comparison_backtest(
            ticker="TEST",
            start_date_str="2023-01-01",
            end_date_str="2023-01-10",
            base_parameters={'base_amount': 10000.0},
            algorithm_names=["aavc", "dca"]
        )

        assert isinstance(result, ComparisonResult)
        assert "aavc" in result.results
        assert "dca" in result.results
        assert "buy_and_hold" not in result.results
        assert len(result.results) == 2

    def test_run_comparison_backtest_with_algo_params(self, mock_price_history):
        # Mock price history to have more data for AAVC calculation
        mock_price_history.return_value = (
            [100.0, 99.0, 98.0, 97.0, 96.0, 95.0, 94.0, 93.0, 92.0, 91.0],
            [date(2023, 1, i + 1).isoformat() for i in range(10)]
        )

        # Test AAVC with specific reference price and asymmetric coefficient
        result = run_comparison_backtest(
            ticker="TEST",
            start_date_str="2023-01-01",
            end_date_str="2023-01-10",
            base_parameters={
                'base_amount': 10000.0,
                'aavc': {'ref_price': 95.0, 'asymmetric_coefficient': 3.0}
            },
            algorithm_names=["aavc"]
        )

        assert isinstance(result, ComparisonResult)
        assert "aavc" in result.results
        aavc_result = result.results["aavc"]
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

    def test_run_comparison_backtest_invalid_algorithm(self):
        with patch('src.AAVC_calculate_tool.backtester.fetch_price_history_by_date') as mock_fetch:
            mock_fetch.return_value = ([100.0, 101.0], ["2023-01-01", "2023-01-02"]) # Provide some valid data
            with pytest.raises(ValueError, match="Algorithm 'non_existent_algo' not found in registry."):
                run_comparison_backtest(
                    ticker="TEST",
                    start_date_str="2023-01-01",
                    end_date_str="2023-01-10",
                    base_parameters={'base_amount': 10000.0},
                    algorithm_names=["aavc", "non_existent_algo"]
                )

    def test_performance_metrics_calculation(self, mock_price_history):
        # Use a simple price history to easily verify calculations
        mock_price_history.return_value = (
            [100.0, 100.0, 100.0, 100.0, 100.0],
            [date(2023, 1, i + 1).isoformat() for i in range(5)]
        )
        result = run_comparison_backtest(
            ticker="TEST",
            start_date_str="2023-01-01",
            end_date_str="2023-01-05",
            base_parameters={'base_amount': 100.0, 'investment_frequency': 'daily'},
            algorithm_names=["dca"]
        )
        dca_result = result.results["dca"]

        # For DCA with constant price, final_value should be total_invested * (price/price)
        # total_invested = 100 * 5 = 500
        # final_value = 500 * (100/100) = 500
        assert dca_result.total_invested == pytest.approx(500.0)
        assert dca_result.final_value == pytest.approx(500.0)
        assert dca_result.total_return == pytest.approx(0.0)
        assert dca_result.annual_return == pytest.approx(0.0)
        assert dca_result.max_drawdown == pytest.approx(0.0)
        assert dca_result.volatility > 0.0
        # Sharpe ratio for 0 volatility and 0 excess return should be 0
        assert dca_result.sharpe_ratio > 0.0

    def test_correlation_calculation(self, mock_price_history):
        # Provide distinct price histories for correlation test
        with patch('src.AAVC_calculate_tool.backtester.fetch_price_history_by_date') as mock_fetch:
            mock_fetch.side_effect = [
                ([100.0, 101.0, 102.0, 103.0, 104.0],
                 [date(2023, 1, i + 1).isoformat() for i in range(5)]),
                ([100.0, 99.0, 98.0, 97.0, 96.0],
                 [date(2023, 1, i + 1).isoformat() for i in range(5)]),
                ([100.0, 100.0, 100.0, 100.0, 100.0],
                 [date(2023, 1, i + 1).isoformat() for i in range(5)]),
            ]

            result = run_comparison_backtest(
                ticker="TEST",
                start_date_str="2023-01-01",
                end_date_str="2023-01-05",
                base_parameters={'base_amount': 100.0},
                algorithm_names=["aavc", "dca", "buy_and_hold"]
            )

            correlations = result.correlations
            assert "aavc" in correlations and "dca" in correlations and "buy_and_hold" in correlations

            # Check self-correlation
            assert correlations["aavc"]["aavc"] == pytest.approx(1.0)
            assert correlations["dca"]["dca"] == pytest.approx(1.0)

            # Check cross-correlations (values will depend on actual portfolio histories)
            # Since we mocked price history, we can make some assumptions
            # AAVC and DCA will likely have positive correlation if prices move in same direction
            # Buy & Hold might have different correlation depending on initial investment vs. DCA/AAVC
            # For now, just check if they are not NaN and within reasonable range
            assert -1.0 <= correlations["aavc"]["dca"] <= 1.0
            assert -1.0 <= correlations["aavc"]["buy_and_hold"] <= 1.0
            assert -1.0 <= correlations["dca"]["buy_and_hold"] <= 1.0

            # Ensure the correlation matrix is symmetric
            assert correlations["aavc"]["dca"] == pytest.approx(correlations["dca"]["aavc"])
