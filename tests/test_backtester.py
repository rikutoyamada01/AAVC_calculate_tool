"""
Tests for the backtester module.
"""

import pytest
from datetime import date
from src.AAVC_calculate_tool.backtester import (
    BacktestParams,
    BacktestResult,
    strategy_aavc,
    strategy_dca,
    strategy_buy_and_hold,
    _run_simulation_engine,
    run_comparison_backtest
)


class TestBacktester:
    """Test cases for backtester module."""
    
    def test_strategy_aavc(self):
        """Test AAVC strategy function."""
        price_path = [100.0, 102.0, 98.0, 105.0]
        params = {
            'base_amount': 10000,
            'reference_price': 100.0,
            'asymmetric_coefficient': 1.0
        }
        
        result = strategy_aavc(price_path, **params)
        assert isinstance(result, float)
        assert result >= 0
    
    def test_strategy_dca(self):
        """Test DCA strategy function."""
        price_path = [100.0, 102.0, 98.0, 105.0]
        params = {'base_amount': 10000}
        
        result = strategy_dca(price_path, **params)
        assert result == 10000
    
    def test_strategy_buy_and_hold(self):
        """Test Buy & Hold strategy function."""
        price_path = [100.0, 102.0, 98.0, 105.0]
        
        # First day
        params = {'total_capital': 50000, 'current_day_index': 0}
        result = strategy_buy_and_hold(price_path, **params)
        assert result == 50000
        
        # Other days
        params = {'total_capital': 50000, 'current_day_index': 1}
        result = strategy_buy_and_hold(price_path, **params)
        assert result == 0.0
    
    def test_run_simulation_engine(self):
        """Test the simulation engine."""
        price_history = [100.0, 102.0, 98.0, 105.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3), date(2023, 1, 4)]
        strategy_params = {'base_amount': 10000}
        
        result = _run_simulation_engine(
            price_history, dates, strategy_dca, strategy_params
        )
        
        assert isinstance(result, dict)
        assert 'final_value' in result
        assert 'total_invested' in result
        assert 'portfolio_history' in result
        assert 'dates' in result
        assert len(result['portfolio_history']) == len(dates)
    
    def test_backtest_params_structure(self):
        """Test BacktestParams structure."""
        params = BacktestParams(
            ticker="AAPL",
            start_date="2023-01-01",
            end_date="2024-01-01",
            base_amount=10000.0,
            reference_price=100.0,
            asymmetric_coefficient=1.0,
            volatility_period=20
        )
        
        assert params['ticker'] == "AAPL"
        assert params['start_date'] == "2023-01-01"
        assert params['end_date'] == "2024-01-01"
        assert params['base_amount'] == 10000.0
        assert params['reference_price'] == 100.0
        assert params['asymmetric_coefficient'] == 1.0
        assert params['volatility_period'] == 20
