# 設定ファイル・投資ログ機能 詳細設計書 (v1.0)

このドキュメントは `03_Configuration_and_Logging.md` を基に、設定ファイルと投資ログ機能の実装に必要な詳細設計を定義する。

## Part A: 設定ファイル管理

### 1. モジュールとファイル構造

設定ファイルの読み込みと解析ロジックは、新しく作成する `AAVC_calculate_tool/config_loader.py` に集約する。

### 2. 依存ライブラリ

- `PyYAML`: YAMLファイルの解析に必要。`pyproject.toml` および `requirements.txt` に追加する。

### 3. データ構造（型定義）

`typing.TypedDict` を用いて、設定ファイルの構造を型として定義し、コードの堅牢性を高める。

```python
# config_loader.py
from typing import TypedDict, List, Optional

class StockConfig(TypedDict):
    ticker: str
    reference_price: float
    base_amount: Optional[float]
    asymmetric_coefficient: Optional[float]

class DefaultSettings(TypedDict):
    base_amount: float
    asymmetric_coefficient: float

class AppConfig(TypedDict):
    default_settings: DefaultSettings
    stocks: List[StockConfig]
```

### 4. 関数定義

`config_loader.py` 内に、以下の主要関数を定義する。

```python
# カスタム例外
class ConfigError(Exception):
    pass

class ConfigNotFoundError(ConfigError):
    pass

class ConfigParseError(ConfigError):
    pass

def load_config(file_path: str) -> AppConfig:
    """YAML設定ファイルを読み込み、型定義に沿った辞書として返す"""
    # ... 実装 ...
```

### 5. 処理フロー (`load_config`)

1.  `pathlib.Path(file_path).exists()` を用いてファイルの存在を確認する。存在しない場合は `ConfigNotFoundError` を送出する。
2.  `try...except` ブロックで `yaml.safe_load()` を呼び出し、YAMLファイルを解析する。
    - `yaml.YAMLError` が発生した場合は、`ConfigParseError` としてラップして再送出する。
3.  解析後の辞書データに対して、必須キー（`default_settings`, `stocks`）の存在を検証する。不足している場合は `ConfigParseError` を送出する。
4.  検証済みの辞書を `AppConfig` 型としてキャストして返却する。

---

## Part B: 投資ログ管理

### 1. モジュールとファイル構造

投資ログの記録ロジックは、新しく作成する `AAVC_calculate_tool/recorder.py` に集約する。

### 2. 依存ライブラリ

- `csv` (Python標準ライブラリ)

### 3. データ構造（型定義）

ログとして書き込む一行のデータを `TypedDict` で定義する。

```python
# recorder.py
from typing import TypedDict

class LogEntry(TypedDict):
    date: str
    ticker: str
    base_amount: float
    reference_price: float
    calculated_investment: float
    # ... その他記録したいパラメータ
```

### 4. 関数定義

`recorder.py` 内に、以下の主要関数を定義する。

```python
# カスタム例外
class LogWriteError(Exception):
    pass

def record_investment(log_entry: LogEntry, file_path: str = "investment_log.csv") -> None:
    """計算結果のログをCSVファイルに追記する"""
    # ... 実装 ...
```

### 5. 処理フロー (`record_investment`)

1.  `pathlib.Path(file_path).exists()` を用いて、ログファイルが既に存在するかを確認する (`file_exists`)。
2.  `try...except` ブロックで、ファイルを追記モード (`'a'`) で開く。
    - `IOError` が発生した場合は、`LogWriteError` としてラップして再送出する。
3.  `csv.DictWriter` を生成する。フィールド名は `LogEntry.__annotations__.keys()` から動的に取得する。
4.  `file_exists` が `False` の場合（つまり新規作成ファイルの場合）、`writer.writeheader()` を呼び出してヘッダー行を書き込む。
5.  `writer.writerow(log_entry)` を呼び出して、新しいログデータを書き込む。
