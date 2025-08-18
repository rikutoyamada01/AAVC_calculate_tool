from datetime import date

from src.AAVC_calculate_tool.backtester import ComparisonResult, EnhancedBacktestResult
from src.AAVC_calculate_tool.display import (
    format_currency,
    format_decimal,
    format_percentage,
    generate_dynamic_summary_table,
)


class TestDisplay:
    """Test cases for display module."""

    def test_format_currency(self):
        assert format_currency(10000) == "\xa510k"
        assert format_currency(1500000) == "\xa51.5M"
        assert format_currency(1500000000) == "\xa51.5B"
        assert format_currency(500) == "\xa5500"

    def test_format_percentage(self):
        assert format_percentage(10.5) == "+10.5%"
        assert format_percentage(-8.2) == "-8.2%"
        assert format_percentage(0.0) == "+0.0%"

    def test_format_decimal(self):
        assert format_decimal(0.12345) == "0.12"
        assert format_decimal(0.567) == "0.57"
        assert format_decimal(2.0) == "2.00"
        assert format_decimal(123.456, 3) == "123.456"

    def test_generate_dynamic_summary_table_simple_mode(self):
        # Create mock EnhancedBacktestResult objects
        aavc_result = EnhancedBacktestResult(
            algorithm_name="aavc",
            final_value=120000.0,
            total_invested=100000.0,
            total_return=20.0,
            annual_return=18.0,
            max_drawdown=5.0,
            volatility=10.0,
            sharpe_ratio=1.5,
            portfolio_history=[1, 2, 3],
            investment_history=[1, 2, 3],
            dates=[date(2023, 1, 1)],
            metadata={}
        )
        dca_result = EnhancedBacktestResult(
            algorithm_name="dca",
            final_value=110000.0,
            total_invested=100000.0,
            total_return=10.0,
            annual_return=9.0,
            max_drawdown=3.0,
            volatility=8.0,
            sharpe_ratio=1.2,
            portfolio_history=[1, 2, 3],
            investment_history=[1, 2, 3],
            dates=[date(2023, 1, 1)],
            metadata={}
        )
        bnh_result = EnhancedBacktestResult(
            algorithm_name="buy_and_hold",
            final_value=130000.0,
            total_invested=100000.0,
            total_return=30.0,
            annual_return=25.0,
            max_drawdown=7.0,
            volatility=12.0,
            sharpe_ratio=1.8,
            portfolio_history=[1, 2, 3],
            investment_history=[1, 2, 3],
            dates=[date(2023, 1, 1)],
            metadata={}
        )

        mock_results = {
            "aavc": aavc_result,
            "dca": dca_result,
            "buy_and_hold": bnh_result
        }

        # Create a mock ComparisonResult
        mock_comparison_result = ComparisonResult(
            results=mock_results,
            summary={
                "best_performer": "buy_and_hold",
                "worst_performer": "dca",
                "best_sharpe": "buy_and_hold",
                "lowest_drawdown": "dca"
            },
            rankings={
                "total_return": ["buy_and_hold", "aavc", "dca"],
                "sharpe_ratio": ["buy_and_hold", "aavc", "dca"],
                "max_drawdown": ["dca", "aavc", "buy_and_hold"],
                "volatility": ["dca", "aavc", "buy_and_hold"]
            },
            correlations={
                "aavc": {"aavc": 1.0, "dca": 0.8, "buy_and_hold": 0.7},
                "dca": {"aavc": 0.8, "dca": 1.0, "buy_and_hold": 0.9},
                "buy_and_hold": {"aavc": 0.7, "dca": 0.9, "buy_and_hold": 1.0}
            }
        )

        table = generate_dynamic_summary_table(mock_comparison_result, mode="simple")

        assert "| Metric(指標)" in table
        assert "| aavc       | dca        | buy_and_hold |" in table
        assert "| Final Value      | \xa5120k      | \xa5110k      | **\xa5130k**  |" in table
        assert "| Ann. Return      | +18.0%     | +9.0%      | **+25.0%** |" in table
        assert "| Max Drawdown     | +5.0%      | **+3.0%**  | +7.0%      |" in table
        assert "| Sharpe Ratio     | 1.50       | 1.20       | **1.80**   |" in table

    def test_generate_dynamic_summary_table_detailed_mode(self):
        # Re-use mock_comparison_result from simple mode test
        aavc_result = EnhancedBacktestResult(
            algorithm_name="aavc",
            final_value=120000.0,
            total_invested=100000.0,
            total_return=20.0,
            annual_return=18.0,
            max_drawdown=5.0,
            volatility=10.0,
            sharpe_ratio=1.5,
            portfolio_history=[1, 2, 3],
            investment_history=[1, 2, 3],
            dates=[date(2023, 1, 1)],
            metadata={}
        )
        dca_result = EnhancedBacktestResult(
            algorithm_name="dca",
            final_value=110000.0,
            total_invested=100000.0,
            total_return=10.0,
            annual_return=9.0,
            max_drawdown=3.0,
            volatility=8.0,
            sharpe_ratio=1.2,
            portfolio_history=[1, 2, 3],
            investment_history=[1, 2, 3],
            dates=[date(2023, 1, 1)],
            metadata={}
        )
        bnh_result = EnhancedBacktestResult(
            algorithm_name="buy_and_hold",
            final_value=130000.0,
            total_invested=100000.0,
            total_return=30.0,
            annual_return=25.0,
            max_drawdown=7.0,
            volatility=12.0,
            sharpe_ratio=1.8,
            portfolio_history=[1, 2, 3],
            investment_history=[1, 2, 3],
            dates=[date(2023, 1, 1)],
            metadata={}
        )

        mock_results = {
            "aavc": aavc_result,
            "dca": dca_result,
            "buy_and_hold": bnh_result
        }

        mock_comparison_result = ComparisonResult(
            results=mock_results,
            summary={
                "best_performer": "buy_and_hold",
                "worst_performer": "dca",
                "best_sharpe": "buy_and_hold",
                "lowest_drawdown": "dca"
            },
            rankings={
                "total_return": ["buy_and_hold", "aavc", "dca"],
                "sharpe_ratio": ["buy_and_hold", "aavc", "dca"],
                "max_drawdown": ["dca", "aavc", "buy_and_hold"],
                "volatility": ["dca", "aavc", "buy_and_hold"]
            },
            correlations={
                "aavc": {"aavc": 1.0, "dca": 0.8, "buy_and_hold": 0.7},
                "dca": {"aavc": 0.8, "dca": 1.0, "buy_and_hold": 0.9},
                "buy_and_hold": {"aavc": 0.7, "dca": 0.9, "buy_and_hold": 1.0}
            }
        )

        table = generate_dynamic_summary_table(mock_comparison_result, mode="detailed")

        assert "## Rankings" in table
        assert "### Total Return" in table
        assert "1. buy_and_hold" in table
        assert "## Correlations" in table
        assert "| Algorithm        | aavc       | dca        | buy_and_hold |" in table
        assert "| aavc             | 1.00       | 0.80       | 0.70       |\n" in table
