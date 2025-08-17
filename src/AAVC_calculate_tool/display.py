"""
Display module for backtest results.

This module handles the formatting and display of backtest comparison results
in the console using markdown tables.
"""

from typing import Dict
from .backtester import BacktestResult


def format_currency(value: float) -> str:
    """Format currency values in a readable format"""
    if value >= 1000000:
        return f"¥{value/1000000:.1f}M"
    elif value >= 1000:
        return f"¥{value/1000:.0f}k"
    else:
        return f"¥{value:.0f}"


def format_percentage(value: float) -> str:
    """Format percentage values"""
    return f"{value:+.1f}%"


def format_decimal(value: float) -> str:
    """Format decimal values"""
    return f"{value:.2f}"


def generate_summary_table(
    results: Dict[str, BacktestResult],
    ticker: str,
    start_date: str,
    end_date: str
) -> str:
    """
    Generate a markdown summary table comparing all strategies.
    
    Args:
        results: Dictionary containing results for all strategies
        ticker: Stock ticker symbol
        start_date: Start date of backtest
        end_date: End date of backtest
        
    Returns:
        Formatted markdown table string
    """
    # Header
    table = f"## Backtest Result: {ticker} ({start_date} to {end_date})\n\n"
    
    # Table header
    table += "| Metric(指標)     | AAVC         | DCA      | Buy & Hold |\n"
    table += "|:-----------------|:-------------|:---------|:-----------|\n"
    
    # Find the best performer for each metric to highlight
    best_final_value = max(results.values(), key=lambda x: x['final_value'])
    best_annual_return = max(results.values(), key=lambda x: x['annual_return'])
    best_total_return = max(results.values(), key=lambda x: x['total_return'])
    best_max_drawdown = min(results.values(), key=lambda x: x['max_drawdown'])
    best_volatility = min(results.values(), key=lambda x: x['volatility'])
    best_sharpe = max(results.values(), key=lambda x: x['sharpe_ratio'])
    
    # Final Value row
    aavc_final = format_currency(results["AAVC"]['final_value'])
    dca_final = format_currency(results["DCA"]['final_value'])
    bnh_final = format_currency(results["Buy & Hold"]['final_value'])
    
    if results["AAVC"]['final_value'] == best_final_value['final_value']:
        aavc_final = f"**{aavc_final}**"
    elif results["DCA"]['final_value'] == best_final_value['final_value']:
        dca_final = f"**{dca_final}**"
    elif results["Buy & Hold"]['final_value'] == best_final_value['final_value']:
        bnh_final = f"**{bnh_final}**"
    
    table += f"| Final Value      | {aavc_final:<11} | {dca_final:<8} | {bnh_final:<10} |\n"
    
    # Annual Return row
    aavc_annual = format_percentage(results["AAVC"]['annual_return'])
    dca_annual = format_percentage(results["DCA"]['annual_return'])
    bnh_annual = format_percentage(results["Buy & Hold"]['annual_return'])
    
    if results["AAVC"]['annual_return'] == best_annual_return['annual_return']:
        aavc_annual = f"**{aavc_annual}**"
    elif results["DCA"]['annual_return'] == best_annual_return['annual_return']:
        dca_annual = f"**{dca_annual}**"
    elif results["Buy & Hold"]['annual_return'] == best_annual_return['annual_return']:
        bnh_annual = f"**{bnh_annual}**"
    
    table += f"| Ann. Return      | {aavc_annual:<11} | {dca_annual:<8} | {bnh_annual:<10} |\n"
    
    # Total Return row
    aavc_total = format_percentage(results["AAVC"]['total_return'])
    dca_total = format_percentage(results["DCA"]['total_return'])
    bnh_total = format_percentage(results["Buy & Hold"]['total_return'])
    
    if results["AAVC"]['total_return'] == best_total_return['total_return']:
        aavc_total = f"**{aavc_total}**"
    elif results["DCA"]['total_return'] == best_total_return['total_return']:
        dca_total = f"**{dca_total}**"
    elif results["Buy & Hold"]['total_return'] == best_total_return['total_return']:
        bnh_total = f"**{bnh_total}**"
    
    table += f"| Total Return     | {aavc_total:<11} | {dca_total:<8} | {bnh_total:<10} |\n"
    
    # Max Drawdown row
    aavc_dd = format_percentage(results["AAVC"]['max_drawdown'])
    dca_dd = format_percentage(results["DCA"]['max_drawdown'])
    bnh_dd = format_percentage(results["Buy & Hold"]['max_drawdown'])
    
    if results["AAVC"]['max_drawdown'] == best_max_drawdown['max_drawdown']:
        aavc_dd = f"**{aavc_dd}**"
    elif results["DCA"]['max_drawdown'] == best_max_drawdown['max_drawdown']:
        dca_dd = f"**{dca_dd}**"
    elif results["Buy & Hold"]['max_drawdown'] == best_max_drawdown['max_drawdown']:
        bnh_dd = f"**{bnh_dd}**"
    
    table += f"| Max Drawdown     | {aavc_dd:<11} | {dca_dd:<8} | {bnh_dd:<10} |\n"
    
    # Volatility row
    aavc_vol = format_percentage(results["AAVC"]['volatility'])
    dca_vol = format_percentage(results["DCA"]['volatility'])
    bnh_vol = format_percentage(results["Buy & Hold"]['volatility'])
    
    if results["AAVC"]['volatility'] == best_volatility['volatility']:
        aavc_vol = f"**{aavc_vol}**"
    elif results["DCA"]['volatility'] == best_volatility['volatility']:
        dca_vol = f"**{dca_vol}**"
    elif results["Buy & Hold"]['volatility'] == best_volatility['volatility']:
        bnh_vol = f"**{bnh_vol}**"
    
    table += f"| Volatility(Ann.) | {aavc_vol:<11} | {dca_vol:<8} | {bnh_vol:<10} |\n"
    
    # Sharpe Ratio row
    aavc_sharpe = format_decimal(results["AAVC"]['sharpe_ratio'])
    dca_sharpe = format_decimal(results["DCA"]['sharpe_ratio'])
    bnh_sharpe = format_decimal(results["Buy & Hold"]['sharpe_ratio'])
    
    if results["AAVC"]['sharpe_ratio'] == best_sharpe['sharpe_ratio']:
        aavc_sharpe = f"**{aavc_sharpe}**"
    elif results["DCA"]['sharpe_ratio'] == best_sharpe['sharpe_ratio']:
        dca_sharpe = f"**{dca_sharpe}**"
    elif results["Buy & Hold"]['sharpe_ratio'] == best_sharpe['sharpe_ratio']:
        bnh_sharpe = f"**{bnh_sharpe}**"
    
    table += f"| Sharpe Ratio     | {aavc_sharpe:<11} | {dca_sharpe:<8} | {bnh_sharpe:<10} |\n"
    
    # Total Invested row
    aavc_invested = format_currency(results["AAVC"]['total_invested'])
    dca_invested = format_currency(results["DCA"]['total_invested'])
    bnh_invested = format_currency(results["Buy & Hold"]['total_invested'])
    
    table += f"| Total Invested   | {aavc_invested:<11} | {dca_invested:<8} | {bnh_invested:<10} |\n"
    
    return table
