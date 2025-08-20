from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, TypedDict

import numpy as np

from .algorithm_registry import InvestmentAlgorithm
from .data_loader import fetch_price_history_by_date
from .plugin_loader import ALGORITHM_REGISTRY


# --- Type Definitions ---
class BacktestParams(TypedDict):
    """Backtest input parameters"""
    ticker: str
    start_date: str
    end_date: str
    base_amount: float
    # Add other common parameters that might be passed to algorithms


@dataclass
class EnhancedBacktestResult:
    """拡張されたバックテスト結果"""
    algorithm_name: str
    final_value: float
    total_invested: float
    total_return: float
    annual_return: float
    max_drawdown: float
    volatility: float
    sharpe_ratio: float
    portfolio_history: List[float]
    investment_history: List[float]
    dates: List[date]
    metadata: Dict[str, Any]


@dataclass
class ComparisonResult:
    """比較結果の集約"""
    results: Dict[str, EnhancedBacktestResult]
    summary: Dict[str, Any]
    rankings: Dict[str, List[str]]
    correlations: Dict[str, Dict[str, float]]


# --- Core Simulation Engine ---
def _run_single_algorithm_backtest(
    algorithm: InvestmentAlgorithm,
    prices: List[float],
    dates: List[date],
    parameters: Dict[str, Any]
) -> EnhancedBacktestResult:
    """単一アルゴリズムのバックテストを実行"""

    shares_owned = 0.0
    total_invested = 0.0
    portfolio_history = []
    investment_history = []

    for i, (price, _current_date) in enumerate(zip(prices, dates)):
        # 投資額を計算
        investment_amount = algorithm.calculate_investment(
            price, prices[:i+1], dates[:i+1], parameters
        )

        # 取引を実行
        if investment_amount > 0:
            shares_bought = investment_amount / price
            shares_owned += shares_bought
            total_invested += investment_amount

        # ポートフォリオ価値を更新
        portfolio_value = shares_owned * price
        portfolio_history.append(portfolio_value)
        investment_history.append(investment_amount)
        

    # パフォーマンス指標を計算
    performance_metrics = _calculate_performance_metrics(
        portfolio_history, investment_history, dates
    )

    return EnhancedBacktestResult(
        algorithm_name=algorithm.get_metadata().name,
        **performance_metrics,
        portfolio_history=portfolio_history,
        investment_history=investment_history,
        dates=dates,
        metadata=parameters
    )


def _calculate_performance_metrics(
    portfolio_history: List[float],
    investment_history: List[float],
    dates: List[date]
) -> Dict[str, Any]:
    """パフォーマンス指標を計算"""

    final_value = portfolio_history[-1] if portfolio_history else 0
    total_invested = sum(investment_history)

    # Handle cases where no investment was made or portfolio value is constant/zero
    if total_invested == 0 or len(portfolio_history) < 2:
        return {
            "final_value": final_value,
            "total_invested": total_invested,
            "total_return": 0.0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0
        }

    # 収益率の計算
    total_return = 0.0
    if total_invested > 0:
        total_return = ((final_value / total_invested - 1) * 100)

    # 年率収益率の計算
    years = (dates[-1] - dates[0]).days / 365.25 if len(dates) > 1 else 0
    annual_return = 0.0
    if years > 0 and total_invested > 0:
        # 負の数に対するべき乗計算を避ける
        if (final_value / total_invested) >= 0:
            annual_return = ((final_value / total_invested) ** (1/years) - 1) * 100

    # 最大下落率の計算
    max_drawdown = _calculate_max_drawdown(portfolio_history)

    # ボラティリティの計算
    # returns = np.diff(np.log(portfolio_history)) if len(portfolio_history) > 1 else [0]
    
    # ログリターンの代わりに単純リターンを計算
    returns = []
    for i in range(1, len(portfolio_history)):
        if portfolio_history[i-1] != 0:
            returns.append((portfolio_history[i] - portfolio_history[i-1]) / portfolio_history[i-1])
        else:
            returns.append(0.0)
    returns = np.array(returns)
    
    volatility = 0.0
    if returns.size > 0:
        volatility = np.std(returns) * np.sqrt(252) * 100

    # シャープレシオの計算
    risk_free_rate = 0.02  # 仮の無リスク金利
    excess_returns = np.array(returns) - risk_free_rate/252
    sharpe_ratio = 0.0
    if np.std(excess_returns) > 0:
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

    return {
        "final_value": final_value,
        "total_invested": total_invested,
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "volatility": volatility,
        "sharpe_ratio": sharpe_ratio
    }


def _calculate_max_drawdown(portfolio_history: List[float]) -> float:
    """最大下落率を計算"""
    if not portfolio_history:
        return 0.0

    peak = portfolio_history[0]
    max_dd = 0.0

    for value in portfolio_history:
        if value > peak:
            peak = value
        # peakが0の場合のゼロ除算を避ける
        if peak == 0:
            drawdown = 0.0
        else:
            drawdown = (peak - value) / peak
        max_dd = max(max_dd, drawdown)

    return max_dd * 100


def _get_algorithm_parameters(
    algorithm_name: str,
    base_parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """アルゴリズム固有のパラメータを取得"""

    algorithm = ALGORITHM_REGISTRY.get_algorithm(algorithm_name)
    if algorithm is None:
        return base_parameters

    metadata = algorithm.get_metadata()
    algorithm_params = {}

    # Start with default parameters from metadata
    for param_name, param_info in metadata.parameters.items():
        if "default" in param_info:
            algorithm_params[param_name] = param_info["default"]

    # Override with general base_parameters
    for param_name, param_value in base_parameters.items():
        if param_name in metadata.parameters:
            algorithm_params[param_name] = param_value

    # Override with algorithm-specific parameters if present
    if algorithm_name in base_parameters and isinstance(base_parameters[algorithm_name], dict):
        for param_name, param_value in base_parameters[algorithm_name].items():
            if param_name in metadata.parameters: # Ensure it's a valid parameter for the algorithm
                algorithm_params[param_name] = param_value

    return algorithm_params


def _analyze_results(results: Dict[str, EnhancedBacktestResult]) -> ComparisonResult:
    """結果を分析して比較結果を生成"""

    # サマリー統計
    summary = {
        "total_algorithms": len(results),
        "best_performer": max(results.keys(), key=lambda k: results[k].total_return),
        "worst_performer": min(results.keys(), key=lambda k: results[k].total_return),
        "best_sharpe": max(results.keys(), key=lambda k: results[k].sharpe_ratio),
        "lowest_drawdown": min(results.keys(), key=lambda k: results[k].max_drawdown)
    }

    # ランキング
    rankings = {
        "total_return": sorted(results.keys(),
                               key=lambda k: results[k].total_return, reverse=True),
        "sharpe_ratio": sorted(results.keys(),
                               key=lambda k: results[k].sharpe_ratio, reverse=True),
        "max_drawdown": sorted(results.keys(), key=lambda k: results[k].max_drawdown),
        "volatility": sorted(results.keys(), key=lambda k: results[k].volatility)
    }

    # 相関分析
    correlations = _calculate_correlations(results)

    return ComparisonResult(
        results=results,
        summary=summary,
        rankings=rankings,
        correlations=correlations
    )


def _calculate_correlations(
    results: Dict[str, EnhancedBacktestResult]
) -> Dict[str, Dict[str, float]]:
    """アルゴリズム間の相関を計算"""

    correlations = {}
    algorithm_names = list(results.keys())

    for i, name1 in enumerate(algorithm_names):
        correlations[name1] = {}
        for j, name2 in enumerate(algorithm_names):
            if i == j:
                correlations[name1][name2] = 1.0
            else:
                # ポートフォリオ履歴の相関を計算
                # 長さが異なる場合は短い方に合わせる
                len1 = len(results[name1].portfolio_history)
                len2 = len(results[name2].portfolio_history)
                min_len = min(len1, len2)

                if min_len == 0:
                    corr = 0.0  # データがない場合は相関なし
                else:
                    history1 = results[name1].portfolio_history[:min_len]
                    history2 = results[name2].portfolio_history[:min_len]

                    # numpy.corrcoefは入力が定数の場合にNaNを返すことがあるため、チェック
                    if np.std(history1) == 0 or np.std(history2) == 0:
                        corr = 0.0
                    else:
                        corr = np.corrcoef(
                            history1,
                            history2
                        )[0, 1]
                        corr = corr if not np.isnan(corr) else 0.0
                correlations[name1][name2] = corr
    return correlations


def run_comparison_backtest(
    ticker: str,
    start_date_str: str,
    end_date_str: str,
    base_parameters: Dict[str, Any],
    algorithm_names: Optional[List[str]] = None
) -> ComparisonResult:
    """複数アルゴリズムでの比較バックテストを実行

    Args:
        ticker: ティッカーシンボル
        start_date_str: 開始日 (YYYY-MM-DD)
        end_date_str: 終了日 (YYYY-MM-DD)
        base_parameters: 全アルゴリズムに適用される基本パラメータ
        algorithm_names: 実行するアルゴリズム名のリスト。Noneの場合、デフォルトアルゴリズムを使用。

    Returns:
        ComparisonResult containing results for all strategies
    """
    # Fetch actual price history for the specified period
    price_history, date_strings = fetch_price_history_by_date(
        ticker,
        start_date_str,
        end_date_str
    )

    # Convert date strings to date objects
    dates = [date.fromisoformat(date_str) for date_str in date_strings]

    if not price_history:
        raise ValueError("No price data available for the specified period.")

    if algorithm_names is None or len(algorithm_names) == 0:
        # デフォルトアルゴリズム
        algorithm_names = ["aavc", "dca", "buy_and_hold"]

    results = {}

    # 各アルゴリズムでバックテストを実行
    for algorithm_name in algorithm_names:
        algorithm = ALGORITHM_REGISTRY.get_algorithm(algorithm_name)
        if algorithm is None:
            raise ValueError(f"Algorithm '{algorithm_name}' not found in registry.")

        # アルゴリズム固有のパラメータを取得
        algo_specific_params = _get_algorithm_parameters(
            algorithm_name, base_parameters
        )

        # Buy & Holdの場合、DCAの総投資額を初期投資額として使用
        if algorithm_name == "buy_and_hold" and "dca" in results:
            dca_total_invested = results["dca"].total_invested
            # Ensure initial_amount is set for Buy & Hold
            algo_specific_params["initial_amount"] = dca_total_invested if dca_total_invested > 0 else algo_specific_params.get("initial_amount", 100000.0)

        # パラメータの妥当性を検証
        if not algorithm.validate_parameters(algo_specific_params):
            raise ValueError(f"Invalid parameters for algorithm '{algorithm_name}'.")

        # バックテストを実行
        result = _run_single_algorithm_backtest(
            algorithm, price_history, dates, algo_specific_params
        )

        results[algorithm_name] = result

    # 結果の集約と分析
    comparison_result = _analyze_results(results)

    return comparison_result
