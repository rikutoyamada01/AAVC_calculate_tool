import os
import tempfile
from datetime import date

import matplotlib
import pytest

matplotlib.use('Agg')  # Use non-interactive backend for testing

from src.AAVC_calculate_tool.backtester import ComparisonResult, EnhancedBacktestResult
from src.AAVC_calculate_tool.plotter import plot_multi_algorithm_chart


class TestPlotter:
    """Test cases for plotter module."""

    @pytest.fixture
    def mock_comparison_result(self):
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
            portfolio_history=[100000, 105000, 110000, 115000, 120000],
            investment_history=[10000, 10000, 10000, 10000, 10000],
            dates=[date(2023, 1, i + 1) for i in range(5)],
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
            portfolio_history=[100000, 102000, 105000, 107000, 110000],
            investment_history=[10000, 10000, 10000, 10000, 10000],
            dates=[date(2023, 1, i + 1) for i in range(5)],
            metadata={}
        )

        # Create a mock ComparisonResult
        return ComparisonResult(
            results={
                "aavc": aavc_result,
                "dca": dca_result
            },
            summary={},
            rankings={},
            correlations={}
        )

    def test_plot_multi_algorithm_chart(self, mock_comparison_result):
        """Test chart generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_multi_algo_chart.png")

            result_path = plot_multi_algorithm_chart(
                mock_comparison_result, output_path
            )

            # Check that file was created
            assert os.path.exists(result_path)
            assert result_path == output_path

            # Check file size (should be non-zero for a valid PNG)
            assert os.path.getsize(result_path) > 0

    def test_plot_multi_algorithm_chart_default_filename(self, mock_comparison_result):
        """Test chart generation with default filename."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            try:
                result_path = plot_multi_algorithm_chart(
                    mock_comparison_result
                )

                # Check that file was created with expected name
                expected_filename = "multi_algorithm_comparison_chart.png"
                assert os.path.basename(result_path) == expected_filename
                assert os.path.exists(result_path)

            finally:
                os.chdir(original_cwd)
