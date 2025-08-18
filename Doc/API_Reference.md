# API Reference

## Overview

This document provides detailed API documentation for all public functions, classes, and modules in the AAVC Calculate Tool.

## Module: calculator

投資アルゴリズムの基底クラスと、AAVC、DCA、Buy & Hold戦略の実装。

### Classes

#### `AAVCStrategy`

```python
class AAVCStrategy(BaseAlgorithm):
    # ... (詳細な実装は省略)
```

**Description**: AAVC (Adaptive Asset Value Control) 戦略を実装したアルゴリズムクラス。

**Inherits from**: `BaseAlgorithm`

**Methods**:
- `get_metadata() -> AlgorithmMetadata`: アルゴリズムのメタデータを返します。
- `calculate_investment(current_price: float, price_history: List[float], date_history: List[date], parameters: Dict[str, Any]) -> float`: AAVC戦略に基づき投資額を計算します。

**Parameters (via `get_metadata`)**:
- `base_amount` (float): 基準投資額。
- `reference_price` (float): 基準価格。
- `asymmetric_coefficient` (float): 非対称係数。

#### `DCAStrategy`

```python
class DCAStrategy(BaseAlgorithm):
    # ... (詳細な実装は省略)
```

**Description**: ドルコスト平均法 (DCA) 戦略を実装したアルゴリズムクラス。

**Inherits from**: `BaseAlgorithm`

**Methods**:
- `get_metadata() -> AlgorithmMetadata`: アルゴリズムのメタデータを返します。
- `calculate_investment(current_price: float, price_history: List[float], date_history: List[date], parameters: Dict[str, Any]) -> float`: DCA戦略に基づき投資額を計算します。

**Parameters (via `get_metadata`)**:
- `base_amount` (float): 毎回の投資額。

#### `BuyAndHoldStrategy`

```python
class BuyAndHoldStrategy(BaseAlgorithm):
    # ... (詳細な実装は省略)
```

**Description**: バイ・アンド・ホールド (Buy & Hold) 戦略を実装したアルゴリズムクラス。

**Inherits from**: `BaseAlgorithm`

**Methods**:
- `get_metadata() -> AlgorithmMetadata`: アルゴリズムのメタデータを返します。
- `calculate_investment(current_price: float, price_history: List[float], date_history: List[date], parameters: Dict[str, Any]) -> float`: Buy & Hold戦略に基づき投資額を計算します。

**Parameters (via `get_metadata`)**:
- `initial_amount` (float): 初回投資額。

---

## Module: algorithm_registry

投資アルゴリズムの登録と管理、および共通インターフェースの定義。

### Classes

#### `AlgorithmMetadata`

```python
@dataclass
class AlgorithmMetadata:
    name: str
    description: str
    version: str
    author: str
    parameters: Dict[str, Any]
    category: str
```

**Description**: アルゴリズムのメタデータを定義するデータクラス。

**Fields**:
- `name` (str): アルゴリズムの名前。
- `description` (str): アルゴリズムの説明。
- `version` (str): アルゴリズムのバージョン。
- `author` (str): アルゴリズムの作者。
- `parameters` (Dict[str, Any]): アルゴリズムが受け入れるパラメータとその型、デフォルト値、説明。
- `category` (str): アルゴリズムのカテゴリ（例: `value_averaging`, `systematic`, `passive`）。

#### `InvestmentAlgorithm`

```python
class InvestmentAlgorithm(Protocol):
    # ... (詳細な実装は省略)
```

**Description**: 全ての投資アルゴリズムが準拠すべき統一インターフェースを定義するプロトコル。

**Methods**:
- `get_metadata() -> AlgorithmMetadata`: アルゴリズムのメタデータを返します。
- `calculate_investment(current_price: float, price_history: List[float], date_history: List[date], parameters: Dict[str, Any]) -> float`: 投資額を計算します。
- `validate_parameters(parameters: Dict[str, Any]) -> bool`: パラメータの妥当性を検証します。

#### `BaseAlgorithm`

```python
class BaseAlgorithm(ABC):
    # ... (詳細な実装は省略)
```

**Description**: `InvestmentAlgorithm` プロトコルを実装するための抽象基底クラス。

**Methods**:
- `get_metadata()`: 抽象メソッド。サブクラスで実装必須。
- `calculate_investment()`: 抽象メソッド。サブクラスで実装必須。
- `validate_parameters()`: デフォルト実装を提供し、サブクラスでオーバーライド可能。

#### `AlgorithmRegistry`

```python
class AlgorithmRegistry:
    # ... (詳細な実装は省略)
```

**Description**: 利用可能な投資アルゴリズムを登録・管理するクラス。

**Methods**:
- `register(algorithm: InvestmentAlgorithm) -> None`: アルゴリズムをレジストリに登録します。
- `get_algorithm(name: str) -> Optional[InvestmentAlgorithm]`: 指定された名前のアルゴリズムインスタンスを返します。
- `list_algorithms() -> List[str]`: 登録されている全てのアルゴリズムの名前のリストを返します。
- `get_metadata(name: str) -> Optional[AlgorithmMetadata]`: 指定されたアルゴリズムのメタデータを返します。

---

## Module: plugin_loader

アルゴリズムレジストリの初期化と、デフォルトアルゴリズムの登録を管理します。

### Functions

#### `initialize_registry`

```python
def initialize_registry():
```

**Description**: アルゴリズムレジストリを初期化し、デフォルトのアルゴリズム（AAVC, DCA, Buy & Hold）を登録します。

**Returns**:
- `AlgorithmRegistry`: 初期化されたアルゴリズムレジストリインスタンス。

### Global Variables

#### `ALGORITHM_REGISTRY`

```python
ALGORITHM_REGISTRY: AlgorithmRegistry
```

**Description**: アプリケーション全体で共有されるグローバルなアルゴリズムレジストリインスタンス。`initialize_registry()` によって初期化されます。

---

## Module: backtester

複数アルゴリズムのバックテスト実行、パフォーマンス分析、結果の集約と比較機能を提供します。

### Classes

#### `EnhancedBacktestResult`

```python
@dataclass
class EnhancedBacktestResult:
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
```

**Description**: 単一アルゴリズムのバックテスト結果を詳細に格納するデータクラス。

**Fields**:
- `algorithm_name` (str): アルゴリズムの名前。
- `final_value` (float): 最終ポートフォリオ評価額。
- `total_invested` (float): 総投資額。
- `total_return` (float): 総リターン率。
- `annual_return` (float): 年率リターン率。
- `max_drawdown` (float): 最大ドローダウン率。
- `volatility` (float): 年率ボラティリティ。
- `sharpe_ratio` (float): シャープレシオ。
- `portfolio_history` (List[float]): 日々のポートフォリオ評価額の履歴。
- `investment_history` (List[float]): 日々の投資額の履歴。
- `dates` (List[date]): バックテスト期間の日付リスト。
- `metadata` (Dict[str, Any]): バックテストに使用されたアルゴリズムのパラメータ。

#### `ComparisonResult`

```python
@dataclass
class ComparisonResult:
    results: Dict[str, EnhancedBacktestResult]
    summary: Dict[str, Any]
    rankings: Dict[str, List[str]]
    correlations: Dict[str, Dict[str, float]]
```

**Description**: 複数アルゴリズムの比較バックテスト結果を集約するデータクラス。

**Fields**:
- `results` (Dict[str, EnhancedBacktestResult]): 各アルゴリズムの`EnhancedBacktestResult`をアルゴリズム名をキーとする辞書。
- `summary` (Dict[str, Any]): 比較全体のサマリー情報（例: 最もパフォーマンスの良いアルゴリズム）。
- `rankings` (Dict[str, List[str]]): 各パフォーマンス指標に基づくアルゴリズムのランキング。
- `correlations` (Dict[str, Dict[str, float]]): アルゴリズム間のポートフォリオ履歴の相関行列。

### Functions

#### `run_comparison_backtest`

```python
def run_comparison_backtest(
    ticker: str,
    start_date_str: str,
    end_date_str: str,
    base_parameters: Dict[str, Any],
    algorithm_names: Optional[List[str]] = None
) -> ComparisonResult
```

**Description**: 指定された銘柄と期間で、複数の投資アルゴリズムのバックテストを実行し、比較結果を返します。

**Parameters**:
- `ticker` (str): バックテスト対象の銘柄のティッカーシンボル。
- `start_date_str` (str): バックテストの開始日（YYYY-MM-DD形式）。
- `end_date_str` (str): バックテストの終了日（YYYY-MM-DD形式）。
- `base_parameters` (Dict[str, Any]): 全てのアルゴリズムに適用される共通の基本パラメータ、またはアルゴリズム固有のパラメータを含む辞書。
- `algorithm_names` (Optional[List[str]]): 実行するアルゴリズム名のリスト。`None`の場合、登録されているデフォルトアルゴリズムを使用します。

**Returns**:
- `ComparisonResult`: 複数アルゴリズムの比較結果を含むオブジェクト。

**Raises**:
- `ValueError`: 指定されたアルゴリズムがレジストリに見つからない場合、またはパラメータが不正な場合。
- `TickerNotFoundError`: 銘柄が見つからない場合。
- `DataFetchError`: 価格データの取得に失敗した場合。

---

## Module: display

バックテスト結果をコンソールに表示するための機能を提供します。

### Functions

#### `generate_dynamic_summary_table`

```python
def generate_dynamic_summary_table(
    comparison_result: ComparisonResult,
    mode: str = "simple"
) -> str
```

**Description**: 複数アルゴリズムの比較結果から、動的なサマリーテーブル（Markdown形式）を生成します。

**Parameters**:
- `comparison_result` (ComparisonResult): 複数アルゴリズムの比較結果オブジェクト。
- `mode` (str, optional): 表示モード。`"simple"`（簡易版）または`"detailed"`（詳細版）を指定。デフォルトは`"simple"`。

**Returns**:
- `str`: 生成されたサマリーテーブルのMarkdown文字列。

**Raises**:
- `ValueError`: 無効な`mode`が指定された場合。

---

## Module: plotter

バックテスト結果をグラフとして可視化するための機能を提供します。

### Functions

#### `plot_multi_algorithm_chart`

```python
def plot_multi_algorithm_chart(
    comparison_result: ComparisonResult,
    output_filename: str = "multi_algorithm_comparison_chart.png"
) -> str
```

**Description**: 複数アルゴリズムのポートフォリオ価値の推移を比較するチャートを生成し、画像ファイルとして保存します。

**Parameters**:
- `comparison_result` (ComparisonResult): 複数アルゴリズムの比較結果オブジェクト。
- `output_filename` (str, optional): 生成されるチャート画像のファイル名。デフォルトは`"multi_algorithm_comparison_chart.png"`。

**Returns**:
- `str`: 保存されたチャート画像の絶対パス。

---

## Module: __main__

コマンドラインインターフェースのエントリーポイント。

### Functions

#### `main`

```python
def main() -> None
```

**Description**: CLIアプリケーションのメインエントリーポイント。コマンドライン引数を解析し、`calc`または`backtest`サブコマンドの処理をディスパッチします。

**CLI Structure**:
```bash
python -m AAVC_calculate_tool [subcommand] [options]
```

**Subcommands**:
- `calc`: 投資額を計算します。
- `backtest`: 複数アルゴリズムのバックテストを実行します。

**`calc` Command Options**:
- `--ticker, -t`: 銘柄コード。
- `--config, -c`: 設定ファイルのパス。
- `--amount, -a`: 基準投資額。
- `--ref-price, -r`: 基準価格。
- `--log-file`: ログファイルのパス。

**`backtest` Command Options**:
- `--ticker, -t`: バックテスト対象の銘柄コード。
- `--start-date`: バックテストの開始日（YYYY-MM-DD）。
- `--end-date`: バックテストの終了日（YYYY-MM-DD）。
- `--amount, -a`: 基準投資額。
- `--algorithms`: 比較するアルゴリズムのカンマ区切りリスト。
- `--algorithm-params`: アルゴリズム固有のパラメータ。
- `--compare-mode`: 比較結果の表示モード（`simple`または`detailed`）。
- `--plot`: 比較チャートを生成するかどうか。

**Example Usage**:
```bash
# 単一銘柄の投資額計算
python -m AAVC_calculate_tool calc --ticker AAPL --amount 10000

# 設定ファイルからの投資額計算
python -m AAVC_calculate_tool calc --config portfolio.yaml

# 複数アルゴリズムのバックテスト
python -m src.AAVC_calculate_tool backtest 
  --ticker AAPL 
  --start-date 2023-01-01 
  --end-date 2024-01-01 
  --amount 10000 
  --algorithms "aavc,dca,buy_and_hold" 
  --plot

# アルゴリズム固有パラメータを指定したバックテスト
python -m src.AAVC_calculate_tool backtest 
  --ticker SPY 
  --start-date 2022-01-01 
  --end-date 2023-01-01 
  --amount 5000 
  --algorithms "aavc" 
  --algorithm-params "aavc:asymmetric_coefficient=2.5"
``` 