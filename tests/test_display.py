"""
Tests for the display module.
"""

import pytest
from src.AAVC_calculate_tool.display import (
    format_currency,
    format_percentage,
    format_decimal,
    generate_summary_table
)
from src.AAVC_calculate_tool.backtester import BacktestResult


class TestDisplay:
    """Test cases for display module."""
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(1000) == "¥1k"
        assert format_currency(1500000) == "¥1.5M"
        assert format_currency(500) == "¥500"
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        assert format_percentage(15.5) == "+15.5%"
        assert format_percentage(-8.2) == "-8.2%"
        assert format_percentage(0.0) == "+0.0%"
    
    def test_format_decimal(self):
        """Test decimal formatting."""
        assert format_decimal(1.234) == "1.23"
        assert format_decimal(0.567) == "0.57"
        assert format_decimal(2.0) == "2.00"
    
    def test_generate_summary_table(self):
        """Test summary table generation."""
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
                "dates": []
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
                "dates": []
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
                "dates": []
            }
        }
        
        table = generate_summary_table(
            mock_results, "AAPL", "2023-01-01", "2024-01-01"
        )
        
        assert "## Backtest Result: AAPL (2023-01-01 to 2024-01-01)" in table
        assert "| Metric(指標)" in table
        assert "| AAVC" in table
        assert "| DCA" in table
        assert "| Buy & Hold" in table
        assert "¥1.5M" in table  # AAVC final value
        assert "¥1.2M" in table  # DCA final value
        assert "¥1.1M" in table  # Buy & Hold final value
