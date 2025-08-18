from typing import Dict, List

from .backtester import ComparisonResult, EnhancedBacktestResult


def format_currency(value: float) -> str:
    """Format currency values in a readable format"""
    if value >= 1_000_000_000:
        return f"\xa5{value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"\xa5{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"\xa5{value/1_000:.0f}k"
    else:
        return f"\xa5{value:.0f}"


def format_percentage(value: float) -> str:
    """Format percentage values"""
    return f"{value:+.1f}%"


def format_decimal(value: float, precision: int = 2) -> str:
    """Format decimal values"""
    return f"{value:.{precision}f}"


def generate_dynamic_summary_table(
    comparison_result: ComparisonResult,
    mode: str = "simple"
) -> str:
    """動的なサマリーテーブルを生成"""

    results = comparison_result.results
    algorithm_names = list(results.keys())

    if mode == "simple":
        return _generate_simple_table(results, algorithm_names)
    elif mode == "detailed":
        return _generate_detailed_table(results, algorithm_names, comparison_result)
    else:
        raise ValueError("Invalid comparison mode. Choose 'simple' or 'detailed'.")


def _generate_simple_table(
    results: Dict[str, EnhancedBacktestResult],
    algorithm_names: List[str]
) -> str:
    """シンプルな比較テーブルを生成"""

    # ヘッダー行
    header = "| Metric(指標)     | " + \
             " | ".join(f"{name:<10}" for name in algorithm_names) + " |"
    separator = "|:-----------------|" + \
                "|".join([":----------"] * len(algorithm_names)) + "|"

    # データ行
    rows = []

    metrics = [
        ("Final Value", "final_value", format_currency, True),
        ("Ann. Return", "annual_return", format_percentage, True),
        ("Total Return", "total_return", format_percentage, True),
        ("Max Drawdown", "max_drawdown", format_percentage, False),
        ("Volatility(Ann.)", "volatility", format_percentage, False),
        ("Sharpe Ratio", "sharpe_ratio", lambda x: format_decimal(x, 2), True),
        ("Total Invested", "total_invested", format_currency, False),
    ]

    for metric_name, attr_name, formatter, higher_is_better in metrics:
        values = []
        for name in algorithm_names:
            values.append(getattr(results[name], attr_name))

        formatted_values = [formatter(v) for v in values]

        # Highlight best performer
        if higher_is_better:
            best_value = max(values)
        else:
            best_value = min(values)

        for i, val in enumerate(values):
            if val == best_value:
                formatted_values[i] = f"**{formatted_values[i]}**"

        rows.append(f"| {metric_name:<16} | " + \
                    " | ".join(f"{v:<10}" for v in formatted_values) + " |")

    # テーブルの組み立て
    table_lines = [header, separator] + rows
    return "\n".join(table_lines)


def _generate_detailed_table(
    results: Dict[str, EnhancedBacktestResult],
    algorithm_names: List[str],
    comparison_result: ComparisonResult
) -> str:
    """詳細な比較テーブルを生成"""
    table_lines = []

    # Simple table part
    table_lines.append(_generate_simple_table(results, algorithm_names))
    table_lines.append("\n")

    # Rankings
    table_lines.append("## Rankings\n")
    for metric, ranked_algos in comparison_result.rankings.items():
        table_lines.append(f"### {metric.replace('_', ' ').title()}\n")
        for i, algo_name in enumerate(ranked_algos):
            table_lines.append(f"{i+1}. {algo_name}\n")
        table_lines.append("\n")

    # Correlations
    table_lines.append("## Correlations\n")
    table_lines.append("| Algorithm        | " + \
                         " | ".join(f"{name:<10}" for name in algorithm_names) + " |\n")
    table_lines.append("|:-----------------|" + \
                        "|".join([":----------"] * len(algorithm_names)) + "|\n")
    for name1 in algorithm_names:
        row_values = []
        for name2 in algorithm_names:
            corr_value = comparison_result.correlations[name1][name2]
            row_values.append(format_decimal(corr_value, 2))
        table_lines.append(f"| {name1:<16} | " + \
                            " | ".join(f"{v:<10}" for v in row_values) + " |\n")
    table_lines.append("\n")

    return "".join(table_lines)
