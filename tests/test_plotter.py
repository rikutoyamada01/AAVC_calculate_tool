"""
Tests for the plotter module.
"""

import pytest
import os
import tempfile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
from src.AAVC_calculate_tool.plotter import plot_comparison_chart
from datetime import date


class TestPlotter:
    """Test cases for plotter module."""
    
    def test_plot_comparison_chart(self):
        """Test chart generation."""
        # Create mock results
        mock_results = {
            "AAVC": {
                "final_value": 1500000.0,
                "total_invested": 1000000.0,
                "total_return": 50.0,
                "annual_return": 25.0,
                "max_drawdown": -15.0,
                "volatility": 18.0,
                "sharpe_ratio": 1.5,
                "portfolio_history": [1000000.0, 1500000.0],
                "dates": [date(2023, 1, 1), date(2023, 1, 2)]
            },
            "DCA": {
                "final_value": 1200000.0,
                "total_invested": 1000000.0,
                "total_return": 20.0,
                "annual_return": 10.0,
                "max_drawdown": -20.0,
                "volatility": 22.0,
                "sharpe_ratio": 0.8,
                "portfolio_history": [1000000.0, 1200000.0],
                "dates": [date(2023, 1, 1), date(2023, 1, 2)]
            },
            "Buy & Hold": {
                "final_value": 1100000.0,
                "total_invested": 1000000.0,
                "total_return": 10.0,
                "annual_return": 5.0,
                "max_drawdown": -25.0,
                "volatility": 25.0,
                "sharpe_ratio": 0.5,
                "portfolio_history": [1000000.0, 1100000.0],
                "dates": [date(2023, 1, 1), date(2023, 1, 2)]
            }
        }
        
        # Test with temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_chart.png")
            
            result_path = plot_comparison_chart(
                mock_results, "AAPL", "2023-01-01", "2024-01-01", output_path
            )
            
            # Check that file was created
            assert os.path.exists(result_path)
            assert result_path == output_path
            
            # Check file size (should be non-zero for a valid PNG)
            assert os.path.getsize(result_path) > 0
    
    def test_plot_comparison_chart_default_filename(self):
        """Test chart generation with default filename."""
        # Create mock results
        mock_results = {
            "AAVC": {
                "final_value": 1500000.0,
                "total_invested": 1000000.0,
                "total_return": 50.0,
                "annual_return": 25.0,
                "max_drawdown": -15.0,
                "volatility": 18.0,
                "sharpe_ratio": 1.5,
                "portfolio_history": [1000000.0, 1500000.0],
                "dates": [date(2023, 1, 1), date(2023, 1, 2)]
            },
            "DCA": {
                "final_value": 1200000.0,
                "total_invested": 1000000.0,
                "total_return": 20.0,
                "annual_return": 10.0,
                "max_drawdown": -20.0,
                "volatility": 22.0,
                "sharpe_ratio": 0.8,
                "portfolio_history": [1000000.0, 1200000.0],
                "dates": [date(2023, 1, 1), date(2023, 1, 2)]
            },
            "Buy & Hold": {
                "final_value": 1100000.0,
                "total_invested": 1000000.0,
                "total_return": 10.0,
                "annual_return": 5.0,
                "max_drawdown": -25.0,
                "volatility": 25.0,
                "sharpe_ratio": 0.5,
                "portfolio_history": [1000000.0, 1100000.0],
                "dates": [date(2023, 1, 1), date(2023, 1, 2)]
            }
        }
        
        # Test with default filename
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result_path = plot_comparison_chart(
                    mock_results, "AAPL", "2023-01-01", "2024-01-01"
                )
                
                # Check that file was created with expected name
                expected_filename = "backtest_chart_AAPL_2023-01-01_to_2024-01-01.png"
                assert os.path.basename(result_path) == expected_filename
                assert os.path.exists(result_path)
                
            finally:
                os.chdir(original_cwd)
