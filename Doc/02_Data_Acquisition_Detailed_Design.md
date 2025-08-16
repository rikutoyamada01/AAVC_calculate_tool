# データ自動取得機能 詳細設計書 (v1.0)

このドキュメントは `02_Data_Acquisition.md` を基に、データ自動取得機能の実装に必要な詳細設計を定義する。

## 1. モジュールとファイル構造

データ取得ロジックは、新しく作成する `AAVC_calculate_tool/data_loader.py` に集約する。

## 2. 依存ライブラリ

- `yfinance`: Yahoo Finance APIラッパー。`pyproject.toml` および `requirements.txt` に追加する必要がある。

## 3. 関数定義

`data_loader.py` 内に、以下の主要関数を定義する。

```python
from functools import lru_cache
import yfinance as yf

# カスタム例外クラス
class DataFetchError(Exception):
    """データ取得に関する汎用的なエラー"""
    pass

class TickerNotFoundError(DataFetchError):
    """ティッカーが見つからない、またはデータが存在しないエラー"""
    pass

@lru_cache(maxsize=32)
def fetch_price_history(ticker: str, period: str = "60d") -> list[float]:
    """指定されたティッカーの時系列価格データを取得する。"""
    # ... 実装 ...
```

- **関数名**: `fetch_price_history`
- **引数**: 
  - `ticker (str)`: 必須。Yahoo Financeのティッカーシンボル。
  - `period (str)`: 任意。データを取得する期間。`yfinance`が受け入れるフォーマット（例: "60d", "3mo", "1y"）。デフォルトは`"60d"`。
- **戻り値**: `list[float]`。終値のリスト。日付の昇順（古い→新しい）でソートされていること。
- **デコレータ**: `@lru_cache(maxsize=32)` を付与し、同一セッション内での重複APIコールを避けるためのインメモリキャッシュを実装する。

## 4. 処理フロー

`fetch_price_history` 関数の内部ロジックは以下の通り。

1.  `yf.Ticker(ticker)` を使って、ティッカーオブジェクトを生成する。
2.  `ticker.history(period=period)` を呼び出して、株価データをPandas DataFrameとして取得する。
3.  取得したDataFrameが空(`empty`)でないか、また `raise_errors=True` でエラーが発生しないかを確認する。
    - 空の場合、`TickerNotFoundError(f"No data found for ticker '{ticker}'")` を送出する。
4.  DataFrameから `'Close'` カラム（終値）を選択する。
5.  `'Close'` カラムのSeriesを、Pythonの `list[float]` に変換する。
6.  リストを返却する。

## 5. エラーハンドリング

ネットワークエラーやAPIからの予期せぬレスポンスに対応するため、`try...except` ブロックで処理を囲む。

```python
def fetch_price_history(ticker: str, period: str = "60d") -> list[float]:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            raise TickerNotFoundError(f"No data found for ticker '{ticker}'")

        return hist['Close'].tolist()

    except TickerNotFoundError: # 自分で定義した例外を再送出
        raise
    except Exception as e:
        # yfinance内部やネットワークの予期せぬエラーをキャッチ
        raise DataFetchError(f"Failed to fetch data for '{ticker}': {e}")
```

- `yf.Ticker` や `history()` が送出する可能性のある一般的な例外 (`Exception`) をキャッチし、カスタム例外の `DataFetchError` としてラップして再送出する。
- これにより、呼び出し元（CLIモジュール）は、このモジュールで定義された2つのカスタム例外 (`TickerNotFoundError`, `DataFetchError`) を捕捉するだけで、詳細なエラーハンドリングが可能になる。
