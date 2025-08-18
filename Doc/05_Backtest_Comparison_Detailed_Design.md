# バックテスト自動比較機能 詳細設計書 (v1.0) - Rev. 2

このドキュメントは `05_Backtest_Comparison.md` を基に、バックテスト自動比較機能の実装に必要な詳細設計を定義する。
(レビュー結果に基づき、保守性向上のため設計をリファクタリング)

## 1. モジュールとファイル構造

### 1.1. 新規作成モジュール
- **`AAVC_calculate_tool/algorithm_registry.py`**: アルゴリズムレジストリとインターフェースの定義。
- **`AAVC_calculate_tool/plugin_loader.py`**: アルゴリズムレジストリの初期化とデフォルトアルゴリズムの登録。

### 1.2. 拡張モジュール
- **`AAVC_calculate_tool/backtester.py`**: 複数アルゴリズム対応のバックテストエンジン、パフォーマンス分析、結果集約機能。
- **`AAVC_calculate_tool/display.py`**: 動的なサマリーテーブル生成ロジック。
- **`AAVC_calculate_tool/plotter.py`**: 複数アルゴリズム対応の比較チャート描画ロジック。
- **`AAVC_calculate_tool/__main__.py`**: 新規CLI引数の処理と、バックテスト実行、結果表示、チャート生成のオーケストレーション。

## 2. データ構造（型定義）の拡張と明確化

複数アルゴリズム比較に対応するため、データ構造を拡張し、明確な型定義を行う。

```python
# AAVC_calculate_tool/backtester.py
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass
from datetime import date

# algorithm_registry.py からインポート
from .algorithm_registry import InvestmentAlgorithm

# --- 入力パラメータの型定義 ---
class BacktestParams(TypedDict):
    """バックテスト入力パラメータ"""
    ticker: str
    start_date: str
    end_date: str
    base_amount: float
    # algorithms, algorithm_params は CLI で処理され、個々のアルゴリズムに渡される

# --- 拡張されたバックテスト結果の型定義 ---
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
```

## 3. `backtester.py` の関数設計

`backtester.py`は、複数アルゴリズムのバックテスト実行、パフォーマンス指標の計算、結果の集約と分析を担う。

### 3.1. `run_comparison_backtest` 関数

CLIから呼び出される主要な関数で、指定されたアルゴリズムリストに対してバックテストを実行し、比較結果を返す。

```python
def run_comparison_backtest(
    ticker: str,
    start_date_str: str,
    end_date_str: str,
    base_parameters: Dict[str, Any],
    algorithm_names: Optional[List[str]] = None
) -> ComparisonResult:
    """複数アルゴリズムでの比較バックテストを実行"""
    # 1. 価格履歴の取得
    # 2. 実行するアルゴリズムの決定 (algorithm_namesがNoneならデフォルトを使用)
    # 3. 各アルゴリズムに対して以下を実行:
    #    a. ALGORITHM_REGISTRYからアルゴリズムインスタンスを取得
    #    b. _get_algorithm_parameters でアルゴリズム固有パラメータを準備
    #    c. パラメータの妥当性検証
    #    d. _run_single_algorithm_backtest を呼び出し、単一アルゴリズムのバックテストを実行
    #    e. 結果をresults辞書に格納
    # 4. _analyze_results を呼び出し、結果を集約・分析してComparisonResultを生成
    # 5. ComparisonResultを返却
```

### 3.2. 内部ヘルパー関数

- **`_run_single_algorithm_backtest`**: 単一の`InvestmentAlgorithm`インスタンスに対してバックテストシミュレーションを実行し、`EnhancedBacktestResult`を生成する。
- **`_calculate_performance_metrics`**: ポートフォリオ履歴、投資履歴、日付リストから、最終資産評価額、総投資額、リターン、最大ドローダウン、ボラティリティ、シャープレシオなどのパフォーマンス指標を計算する。
- **`_calculate_max_drawdown`**: ポートフォリオ履歴から最大ドローダウンを計算する。
- **`_get_algorithm_parameters`**: アルゴリズムのメタデータとCLIから渡されたパラメータを基に、アルゴリズム固有のパラメータ辞書を生成する。
- **`_analyze_results`**: 各アルゴリズムの`EnhancedBacktestResult`を集約し、サマリー統計、ランキング、相関分析を含む`ComparisonResult`を生成する。
- **`_calculate_correlations`**: 各アルゴリズムのポートフォリオ履歴間の相関を計算する。

## 4. `plotter.py` / `display.py` の設計

これらのモジュールは、`ComparisonResult` オブジェクトを受け取り、その内容を基に表示やチャート生成を行う。

### 4.1. `display.py`

- **`generate_dynamic_summary_table(comparison_result: ComparisonResult, mode: str) -> str`**:
  - `ComparisonResult` を受け取り、`mode` (`simple` または `detailed`) に応じて動的なサマリーテーブル（Markdown形式）を生成する。
  - `detailed` モードでは、パフォーマンス指標のランキングやアルゴリズム間の相関分析結果も表示する。

### 4.2. `plotter.py`

- **`plot_multi_algorithm_chart(comparison_result: ComparisonResult, output_filename: str) -> str`**:
  - `ComparisonResult` を受け取り、複数アルゴリズムのポートフォリオ価値の推移を比較するチャートを生成する。
  - チャートはPNG画像として `output_filename` に保存される。

## 5. CLI (`__main__.py`) の修正

`__main__.py`は、新しいCLI引数に対応し、複数アルゴリズム比較バックテストのオーケストレーションを行う。

### 5.1. 引数パース処理
1. `argparse` を使用して、`backtest` サブコマンドの以下の引数をパースする:
   - 必須引数: `--ticker`, `--start-date`, `--end-date`, `--amount`
   - オプション引数: `--algorithms`, `--algorithm-params`, `--compare-mode`, `--plot`
2. `--algorithms` が指定された場合、カンマ区切りでアルゴリズム名のリストを生成する。
3. `--algorithm-params` が指定された場合、`parse_algorithm_parameters` 関数（`__main__.py`内に実装）を使用して、アルゴリズム固有のパラメータ辞書を生成する。

### 5.2. バックテスト実行
1. `backtester.run_comparison_backtest` 関数を呼び出す。
   - `ticker`, `start_date_str`, `end_date_str`, `base_parameters` (CLIの`--amount`と`--algorithm-params`から構築), `algorithm_names` (CLIの`--algorithms`から構築) を渡す。

### 5.3. 結果表示処理
1. `display.generate_dynamic_summary_table(comparison_result, mode=args.compare_mode)` を呼び出し、サマリーテーブルを生成する。
2. 生成されたテーブルをコンソールに出力する。

### 5.4. チャート生成処理（`--plot` 指定時）
1. `plotter.plot_multi_algorithm_chart(comparison_result, output_filename)` を呼び出し、比較チャートを生成し、ファイルに保存する。
2. 保存されたチャートのパスをコンソールに表示する。

### 5.5. エラーハンドリング
- `TickerNotFoundError`, `DataFetchError`, `ValueError` などの例外を適切に捕捉し、ユーザーフレンドリーなエラーメッセージを表示して終了する。
