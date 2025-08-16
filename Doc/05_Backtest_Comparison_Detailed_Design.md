# バックテスト自動比較機能 詳細設計書 (v1.0) - Rev. 2

このドキュメントは `05_Backtest_Comparison.md` を基に、バックテスト自動比較機能の実装に必要な詳細設計を定義する。
(レビュー結果に基づき、保守性向上のため設計をリファクタリング)

## 1. モジュールとファイル構造 (変更なし)

- **`AAVC_calculate_tool/backtester.py`**: コアなバックテストエンジンと各戦略ロジックを配置。
- **`AAVC_calculate_tool/plotter.py`**: チャート描画ロジック。
- **`AAVC_calculate_tool/display.py`**: コンソール表示ロジック。

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

1.  引数をパースし、`BacktestParams` オブジェクトを作成する。
2.  `backtester.run_comparison_backtest(params)` を呼び出し、`results` を取得する。
3.  `display.generate_summary_table(results)` を呼び出し、整形されたテーブルを `print` する。
4.  `--plot` フラグが指定されている場合:
    a. `plotter.plot_comparison_chart(results, output_path=...)` を呼び出してチャートを保存する。
    b. `print(f"Chart saved to {os.path.abspath(output_path)}")` のように、保存したチャートの**絶対パス**をユーザーに通知する。
