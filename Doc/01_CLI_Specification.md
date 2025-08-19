# 1. コマンドラインインターフェース（CLI）要件定義

## 1.1. 目的
このドキュメントは、AAVC計算ツールのコマンドラインインターフェース（CLI）の仕様を定義する。
利用者がターミナルから直接、かつ容易に投資額計算を実行できるようにすることを目的とする。

## 1.2. 主要機能
- 銘柄コードを指定して、単一銘柄の投資額を計算する機能。
- 基準投資額や基準価格などのパラメータをコマンドライン引数で指定できる機能。
- 設定ファイル（後述）を利用して計算を実行する機能。
- 計算結果を標準出力に分かりやすく表示する機能。

## 1.3. コマンド仕様（案）

### `calc` コマンド: 投資額計算

単一銘柄の投資額を計算、または設定ファイルに基づいて複数の銘柄の投資額を計算します。

#### 単一銘柄の計算
```bash
python -m src.AAVC_calculate_tool calc --ticker <TICKER_SYMBOL> --amount <BASE_AMOUNT> [--ref-price <REFERENCE_PRICE>] [--asymmetric-coefficient <COEFFICIENT>] [--max-multiplier <MULTIPLIER>] [--log-file <LOG_FILE_PATH>]
```

- `--ticker`, `-t`: 必須。計算対象の銘柄のティッカーシンボル（例: "AAPL", "7203.T"）。
- `--amount`, `-a`: 必須。基準投資額（例: 10000）。
- `--ref-price`, `-r`: オプション。基準価格。指定しない場合は、過去のデータから自動で設定されます。
- `--asymmetric-coefficient`: オプション。AAVC計算の非対称性係数（デフォルト: 2.0）。
- `--max-multiplier`: オプション。AAVC計算の最大投資額の基準額に対する倍率（デフォルト: 3.0）。
- `--ref-ma-period`: オプション。基準価格として使用する移動平均の期間（デフォルト: 200）。
- `--log-file`: オプション。投資ログを記録するCSVファイルのパス（デフォルト: `investment_log.csv`）。
- `--algorithms`: オプション。使用するアルゴリズムのカンマ区切りリスト（例: `AAVC,SMA`）。指定しない場合、デフォルトのアルゴリズム（AAVC）が使用されます。
- `--algorithm-params`: オプション。アルゴリズム固有のパラメータをJSON形式で指定します（例: `'{"SMA": {"period": 50}}'`）。
- `--compare-mode`: オプション。比較モードを有効にし、各アルゴリズムの結果を並べて表示します。

#### 設定ファイルを利用した計算
```bash
python -m src.AAVC_calculate_tool calc --config <PATH_TO_CONFIG_FILE>
```
- `--config`, `-c`: 必須。設定ファイルのパスを指定します。設定ファイル内の全銘柄を対象に計算を実行します。

### `backtest` コマンド: 複数アルゴリズム比較バックテスト

指定された期間と銘柄で、複数の投資アルゴリズムのバックテストを実行し、パフォーマンスを比較します。

```bash
python -m src.AAVC_calculate_tool backtest \
  --ticker <TICKER_SYMBOL> \
  --start-date <YYYY-MM-DD> \
  --end-date <YYYY-MM-DD> \
  --amount <BASE_AMOUNT> \
  [--algorithms <ALGO1,ALGO2,...>] \
  [--algorithm-params <ALGO:PARAM=VAL,...>] \
  [--compare-mode <simple|detailed>] \
  [--plot]
```

- `--ticker`, `-t`: 必須。バックテスト対象の銘柄のティッカーシンボル。
- `--start-date`: 必須。バックテストの開始日（YYYY-MM-DD形式）。
- `--end-date`: 必須。バックテストの終了日（YYYY-MM-DD形式）。
- `--amount`, `-a`: 必須。基準投資額。
- `--algorithms`: オプション。比較するアルゴリズムのカンマ区切りリスト（例: `aavc,dca,buy_and_hold`）。指定しない場合、登録されている全てのアルゴリズム（AAVC, DCA, Buy & Hold）がデフォルトで実行されます。
- `--algorithm-params`: オプション。アルゴリズム固有のパラメータを指定します。形式は `algo_name:param1=val1;param2=val2,algo_name2:paramA=valA` のように、アルゴリズム名とパラメータをコロンで区切り、複数のパラメータはセミコロンで区切ります。
- `--compare-mode`: オプション。比較結果の表示モード（`simple` または `detailed`）。デフォルトは `simple` です。
- `--plot`: オプション。比較チャートを生成し、ファイルに保存します。


## 1.4. 出力形式

### 投資額計算 (`calc` コマンド) の出力

**単一アルゴリズムの場合:**
```
--- Calculation Result ---
Ticker: AAPL
Date: 2025-08-17
Algorithm: AAVC
Investment Amount: ¥12,500
--------------------------
```

**複数アルゴリズム比較モードの場合 (`--compare-mode`):**
```
--- Calculation Result ---
Ticker: AAPL
Date: 2025-08-17
Algorithm: AAVC
Investment Amount: ¥12,500
--------------------------

--- Calculation Result ---
Ticker: AAPL
Date: 2025-08-17
Algorithm: SMA
Investment Amount: ¥10,000
--------------------------

--- Comparison Result ---
Ticker: AAPL
Date: 2025-08-17
AAVC Investment Amount: ¥12,500
SMA Investment Amount: ¥10,000
--------------------------
```

### バックテスト (`backtest` コマンド) の出力

バックテストの結果は、比較対象のアルゴリズムのパフォーマンス指標をまとめた動的なサマリーテーブルとして表示されます。`--compare-mode detailed` を指定した場合は、ランキングや相関分析などの詳細情報も含まれます。

また、`--plot` オプションを指定した場合は、ポートフォリオ価値の推移を比較するチャートが画像ファイルとして保存され、その保存パスが表示されます。

**サマリーテーブルの例 (simple モード):**

```
| Metric(指標)     | aavc       | dca        | buy_and_hold |
|:-----------------|:----------|:----------|:----------|
| Final Value      | ¥120,000   | ¥115,000   | **¥130,000** |
| Ann. Return      | +15.0%     | +12.0%     | **+20.0%** |
| Total Return     | +20.0%     | +18.0%     | **+25.0%** |
| Max Drawdown     | 10.0%      | 8.0%       | **5.0%**   |
| Volatility(Ann.) | 12.0%      | 10.0%      | **8.0%**   |
| Sharpe Ratio     | 1.20       | 1.10       | **1.50**   |
| Total Invested   | ¥100,000   | ¥100,000   | ¥100,000   |
```

**チャート出力の例:**

```
Chart saved to: /path/to/multi_algorithm_comparison_AAPL_2023-01-01_2024-01-01.png
```

## 1.5. 考慮事項
- エラーハンドリング（例: 銘柄コードが見つからない、API通信失敗）。
- ヘルプメッセージ（`-h`, `--help`）の実装。
