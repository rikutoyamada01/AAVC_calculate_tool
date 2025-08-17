# バックテスト自動比較機能 詳細設計書 (v1.0) - Rev. 2

このドキュメントは `05_Backtest_Comparison.md` を基に、バックテスト自動比較機能の実装に必要な詳細設計を定義する。
(レビュー結果に基づき、保守性向上のため設計をリファクタリング)

## 1. モジュールとファイル構造

### 1.1. 新規作成モジュール
- **`AAVC_calculate_tool/backtester.py`**: コアなバックテストエンジンと各戦略ロジックを配置。
- **`AAVC_calculate_tool/plotter.py`**: チャート描画ロジック。
- **`AAVC_calculate_tool/display.py`**: コンソール表示ロジック。

### 1.2. 拡張モジュール
- **`AAVC_calculate_tool/data_loader.py`**: 日付範囲指定による価格データ取得機能を追加
- **`AAVC_calculate_tool/__main__.py`**: `backtest` サブコマンドの実装

## 2. データ構造（型定義）の拡張と明確化

曖昧な`dict`を避け、パラメータと結果に明確な型を定義する。

```python
# backtester.py
from typing import TypedDict, List, Callable, Protocol

# --- 入力パラメータの型定義 ---
class BacktestParams(TypedDict):
    ticker: str
    start_date: str
    end_date: str
    base_amount: float
    reference_price: float
    asymmetric_coefficient: float
    volatility_period: int

# --- 戦略関数の型定義 ---
class InvestmentStrategy(Protocol):
    """投資戦略関数のインターフェース定義"""
    def __call__(self, price_path: List[float], **kwargs) -> float:
        ...

# --- 結果の型定義 ---
class BacktestResult(TypedDict):
    # ... パフォーマンス指標 ...
    portfolio_history: List[float]
    dates: List[datetime.date]
```

## 3. `backtester.py` の関数設計 (リファクタリング)

コードの重複を避けるため、汎用的なシミュレーションエンジンと、個別の戦略関数に分離する。

### 3.1. 汎用シミュレーションエンジン

```python
def _run_simulation_engine(
    price_history: List[float],
    dates: List[datetime.date],
    strategy_func: InvestmentStrategy,
    strategy_params: dict
) -> BacktestResult:
    """単一戦略のバックテストを実行する汎用エンジン"""
    # 1. 初期化 (shares_owned, total_invested など)
    # 2. メインループ: 日付と価格でループ
    #    a. 戦略関数に必要なデータを準備 (価格のスライスなど)
    #    b. investment_amount = strategy_func(data, **strategy_params)
    #    c. 取引を実行し、保有株数や総投資額を更新
    #    d. 日々の資産評価額を記録
    # 3. ループ終了後、全パフォーマンス指標を計算
    # 4. BacktestResultオブジェクトを返却
```

### 3.2. 個別の戦略関数

エンジンに渡すための、シンプルな責務を持つ関数群。

```python
def strategy_aavc(price_path: List[float], **params) -> float:
    """AAVC戦略に基づき投資額を返す"""
    return calculate_aavc_investment(price_path, **params)

def strategy_dca(price_path: List[float], **params) -> float:
    """DCA戦略: 常に基準額を返す"""
    return params['base_amount']

def strategy_buy_and_hold(price_path: List[float], **params) -> float:
    """B&H戦略: 初日のみ全額投資し、以降は0を返す"""
    if params['current_day_index'] == 0:
        return params['total_capital']
    return 0.0
```

### 3.3. オーケストレーション関数

```python
def run_comparison_backtest(params: BacktestParams) -> dict[str, BacktestResult]:
    """全戦略のバックテストを統括し、結果を辞書で返す"""
    price_history, dates = fetch_price_history(params['ticker'], ...)
    
    # AAVCを最初に実行し、総投資額を決定
    aavc_result = _run_simulation_engine(..., strategy_func=strategy_aavc, ...)
    
    # DCAを実行
    dca_result = _run_simulation_engine(..., strategy_func=strategy_dca, ...)
    
    # B&Hを実行 (AAVCの総投資額を利用)
    bnh_params = {'total_capital': aavc_result['total_invested']}
    bnh_result = _run_simulation_engine(..., strategy_func=strategy_buy_and_hold, strategy_params=bnh_params)
    
    return {"AAVC": aavc_result, "DCA": dca_result, "Buy & Hold": bnh_result}
```

## 4. `plotter.py` / `display.py` の設計 (変更なし)

これらのモジュールは、`BacktestResult` を受け取るというインターフェースに変わりはないため、設計の変更は不要。

## 5. CLI (`__main__.py`) の修正

`backtest` サブコマンドの処理フローを、新しいインターフェースに合わせて修正する。

### 5.1. 引数パース処理
1. 必須引数の検証（`--ticker`, `--start-date`, `--end-date`, `--amount`）
2. オプション引数の設定（デフォルト値の適用）
3. `BacktestParams` オブジェクトの作成

### 5.2. データ取得処理
1. `fetch_price_history_by_date()` による指定期間の価格データ取得
2. 日付文字列から `date` オブジェクトへの変換

### 5.3. バックテスト実行
1. `backtester.run_comparison_backtest(params)` の呼び出し
2. 3つの戦略（AAVC、DCA、Buy & Hold）の並行実行

### 5.4. 結果表示処理
1. `display.generate_summary_table(results)` によるサマリーテーブル生成
2. コンソールへの出力

### 5.5. チャート生成処理（`--plot` 指定時）
1. `plotter.plot_comparison_chart()` によるチャート生成
2. ファイル保存と絶対パスの表示

### 5.6. エラーハンドリング
1. 各段階での適切なエラーキャッチ
2. ユーザーフレンドリーなエラーメッセージの表示
3. 適切な終了コードの設定
