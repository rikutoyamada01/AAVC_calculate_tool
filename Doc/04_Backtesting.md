# 4. バックテスト機能 要件定義

## 4.1. 目的
このドキュメントは、AAVCアルゴリズムの過去データにおけるパフォーマンスを検証するバックテスト機能の仕様を定義する。
投資戦略の有効性を客観的に評価し、パラメータ調整の判断材料を提供することを目的とする。

## 4.2. 主要機能
- 指定された銘柄と期間で、AAVC戦略の投資シミュレーションを実行する機能。
- シミュレーション結果として、主要なパフォーマンス指標を表示する機能。
- 比較対象として、同期間のドルコスト平均法やBuy & Hold戦略のパフォーマンスも算出する機能。

## 4.3. コマンド仕様（案）

### 単一銘柄のバックテスト
```bash
python -m AAVC_calculate_tool backtest --ticker <TICKER_SYMBOL> --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD> [options]
```
- `--ticker`: 必須。
- `--start-date`, `--end-date`: 必須。バックテストの対象期間。
- `[options]`: `--amount`, `--ref-price` などのパラメータを任意で指定。

### 設定ファイルに基づく一括バックテスト
```bash
python -m AAVC_calculate_tool backtest --config <PATH_TO_CONFIG> --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD>
```
- `--config`: 必須。`config.yaml`など設定ファイルのパスを指定する。
- `--start-date`, `--end-date`: 必須。設定ファイル内の全銘柄に適用する共通のバックテスト期間。

## 4.4. パフォーマンス指標（案）
- **最終資産評価額** (Final Portfolio Value)
- **トータルリターン** (Total Return)
- **年率リターン** (Annualized Return)
- **最大ドローダウン** (Max Drawdown): 最高資産額からの最大下落率
- **シャープレシオ** (Sharpe Ratio): リスク調整後リターン

## 4.5. 出力形式（案）
- コンソールへのサマリー表示。
- （オプション）結果をグラフ（資産推移など）としてファイル出力する機能。

## 4.6. 考慮事項
- 配当や株式分割の考慮。
- 取引手数料（コスト）の考慮。
- 長期間のデータ取得に伴うパフォーマンス。
