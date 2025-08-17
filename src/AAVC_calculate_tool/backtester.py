"""
Backtest engine and investment strategies for AAVC comparison.

This module provides the core backtesting functionality to compare AAVC strategy
with DCA (Dollar Cost Averaging) and Buy & Hold strategies.
"""

from datetime import date
from typing import TypedDict, List, Callable, Protocol, Dict, Any
import numpy as np
from .calculator import calculate_aavc_investment
from .data_loader import fetch_price_history_by_date


# --- Type Definitions ---
class BacktestParams(TypedDict):
    """Backtest input parameters"""
    ticker: str
    start_date: str
    end_date: str
    base_amount: float
    reference_price: float
    asymmetric_coefficient: float
    volatility_period: int


class BacktestResult(TypedDict):
    """Backtest result data"""
    final_value: float
    total_invested: float
    total_return: float
    annual_return: float
    max_drawdown: float
    volatility: float
    sharpe_ratio: float
    portfolio_history: List[float]
    dates: List[date]


class InvestmentStrategy(Protocol):
    """Investment strategy function interface"""
    def __call__(self, price_path: List[float], **kwargs) -> float:
        ...


# --- Strategy Functions ---
def strategy_aavc(price_path: List[float], **params) -> float:
    """AAVC strategy: calculate investment based on AAVC algorithm"""
    return calculate_aavc_investment(
        price_path=price_path,
        base_amount=params['base_amount'],
        reference_price=params['reference_price'],
        asymmetric_coefficient=params.get('asymmetric_coefficient', 1.0)
    )


def strategy_dca(price_path: List[float], **params) -> float:
    """DCA strategy: always invest the base amount"""
    return params['base_amount']


def strategy_buy_and_hold(price_path: List[float], **params) -> float:
    """Buy & Hold strategy: invest total capital on first day only"""
    if params['current_day_index'] == 0:
        return params['total_capital']
    return 0.0


# --- Core Simulation Engine ---
def _run_simulation_engine(
    price_history: List[float],
    dates: List[date],
    strategy_func: InvestmentStrategy,
    strategy_params: Dict[str, Any]
) -> BacktestResult:
    """
    Run a single strategy backtest using the generic simulation engine.
    
    Args:
        price_history: List of daily prices
        dates: List of corresponding dates
        strategy_func: Strategy function to execute
        strategy_params: Parameters for the strategy
        
    Returns:
        BacktestResult containing performance metrics and history
    """
    shares_owned = 0.0
    total_invested = 0.0
    portfolio_history = []
    
    for i, (price, current_date) in enumerate(zip(price_history, dates)):
        # Prepare strategy parameters
        current_params = strategy_params.copy()
        current_params['current_day_index'] = i
        
        # Get investment amount from strategy
        investment_amount = strategy_func(price_history[:i+1], **current_params)
        
        # Execute trade
        if investment_amount > 0:
            shares_bought = investment_amount / price
            shares_owned += shares_bought
            total_invested += investment_amount
        
        # Calculate current portfolio value
        current_value = shares_owned * price
        portfolio_history.append(current_value)
    
    # Calculate performance metrics
    final_value = portfolio_history[-1]
    total_return = ((final_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    # Annual return (simple approximation)
    years = len(dates) / 252  # Assuming 252 trading days per year
    annual_return = ((final_value / total_invested) ** (1 / years) - 1) * 100 if total_invested > 0 and years > 0 else 0
    
    # Max drawdown
    peak = portfolio_history[0]
    max_drawdown = 0
    for value in portfolio_history:
        if value > peak:
            peak = value
        drawdown = (peak - value) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # Volatility (annualized)
    returns = []
    for i in range(1, len(portfolio_history)):
        if portfolio_history[i-1] > 0:
            daily_return = (portfolio_history[i] - portfolio_history[i-1]) / portfolio_history[i-1]
            returns.append(daily_return)
    
    volatility = np.std(returns) * np.sqrt(252) * 100 if returns else 0
    
    # Sharpe ratio (assuming 0% risk-free rate for simplicity)
    sharpe_ratio = (np.mean(returns) * 252) / (np.std(returns) * np.sqrt(252)) if returns and np.std(returns) > 0 else 0
    
    return BacktestResult(
        final_value=final_value,
        total_invested=total_invested,
        total_return=total_return,
        annual_return=annual_return,
        max_drawdown=max_drawdown,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        portfolio_history=portfolio_history,
        dates=dates
    )


# --- Main Comparison Function ---
def run_comparison_backtest(params: BacktestParams) -> Dict[str, BacktestResult]:
    """
    Run backtest comparison for all three strategies.
    
    Args:
        params: Backtest parameters
        
    Returns:
        Dictionary containing results for all strategies
    """
    # Fetch actual price history for the specified period
    price_history, date_strings = fetch_price_history_by_date(
        params['ticker'], 
        params['start_date'], 
        params['end_date']
    )
    
    # Convert date strings to date objects
    dates = [date.fromisoformat(date_str) for date_str in date_strings]
    
    # Run AAVC strategy first to get total investment amount
    aavc_params = {
        'base_amount': params['base_amount'],
        'reference_price': params['reference_price'],
        'asymmetric_coefficient': params.get('asymmetric_coefficient', 1.0)
    }
    aavc_result = _run_simulation_engine(
        price_history, dates, strategy_aavc, aavc_params
    )
    
    # Run DCA strategy
    dca_params = {'base_amount': params['base_amount']}
    dca_result = _run_simulation_engine(
        price_history, dates, strategy_dca, dca_params
    )
    
    # Run Buy & Hold strategy using AAVC's total investment
    bnh_params = {'total_capital': aavc_result['total_invested']}
    bnh_result = _run_simulation_engine(
        price_history, dates, strategy_buy_and_hold, bnh_params
    )
    
    return {
        "AAVC": aavc_result,
        "DCA": dca_result,
        "Buy & Hold": bnh_result
    }
