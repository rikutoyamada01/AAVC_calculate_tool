# CLI 詳細設計書 (v1.0) - Rev. 2

(レビュー結果に基づき、`backtest`コマンドの追加と設定ファイル連携を反映)

## 1. ファイル構造 (変更なし)

CLIのエントリーポイント（実行起点）は、`AAVC_calculate_tool/__main__.py` に配置する。

## 2. 使用モジュール (変更なし)

- **引数解析**: `argparse` (Python標準ライブラリ)
- **設定ファイル解析**: `PyYAML`

## 3. 引数定義 (サブコマンド方式に刷新)

`argparse`の**サブパーサー機能**を利用し、`calc`と`backtest`の2つのサブコマンドを定義する。

```bash
# 使用法
python -m AAVC_calculate_tool <command> [<args>]
```

### 3.1. `calc` サブコマンド

日々の投資額を計算するためのコマンド。

**コマンド仕様:**
```bash
# 単一銘柄モード
python -m AAVC_calculate_tool calc --ticker <TICKER> --amount <AMOUNT> [options]

# 設定ファイルモード
python -m AAVC_calculate_tool calc --config <PATH_TO_CONFIG>
```
- `--ticker`と`--config`は相互排他的。

### 3.2. `backtest` サブコマンド

バックテストを実行するためのコマンド。

**コマンド仕様:**
```bash
# 単一銘柄モード
python -m AAVC_calculate_tool backtest --ticker <TICKER> --start-date <DATE> --end-date <DATE> [options]

# 設定ファイルモード
python -m AAVC_calculate_tool backtest --config <PATH_TO_CONFIG> --start-date <DATE> --end-date <DATE> [options]
```
- `--ticker`と`--config`は相互排他的。
- `--start-date`, `--end-date`は両モードで必須。
- `[options]`には`--plot`フラグや、`--amount`等のAAVCパラメータを含む。

## 4. 処理フロー

`__main__.py`のメインロジックは以下の通り。

1.  `argparse`で、まずサブコマンド(`calc` or `backtest`)を特定する。
2.  **`calc`コマンドが指定された場合**:
    a. `calc`用の引数をパースする。
    b. (旧設計書4項の処理フローに沿って、日々の投資額計算を実行)
3.  **`backtest`コマンドが指定された場合**:
    a. `backtest`用の引数をパースする。
    b. **`--config`が指定されていれば (設定ファイルモード)**:
        i. `config_loader.load_config`で設定ファイルを読み込む。
        ii. `stocks`リストをループし、各`stock`に対して`backtester.run_comparison_backtest`を呼び出す。この際、CLI引数の`start-date`等を共通パラメータとして渡す。
        iii. `display.generate_summary_table`で結果を整形し、銘柄ごとに出力する。
    c. **`--ticker`が指定されていれば (単一銘柄モード)**:
        i. CLI引数から`BacktestParams`オブジェクトを作成する。
        ii. `backtester.run_comparison_backtest`を一度だけ呼び出す。
        iii. 結果を整形して出力する。
    d. `--plot`フラグがあれば、各バックテストの最後に`plotter.plot_comparison_chart`を呼び出す。

## 5. 基準価格の自動設定ロジック (変更なし)

`--ref-price` 引数が指定されなかった場合、取得した時系列価格リストの最初の要素の価格を基準価格として自動的に使用する。

## 6. エラーハンドリング (変更なし)

各機能モジュールから送出されるカスタム例外を`__main__.py`で捕捉し、エラーメッセージを表示して終了する。