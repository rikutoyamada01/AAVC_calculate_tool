# バックテスト比較機能 使い方ガイド

## 🚀 はじめに

AAVC戦略の有効性を客観的に評価するため、標準的な投資戦略（ドルコスト平均法、一括投資）とパフォーマンスを直接比較する機能です。

## 📋 基本的な使い方

### 1. 基本的なバックテスト

#### Linux/macOS (bash)
```bash
python -m src.AAVC_calculate_tool backtest \
  --ticker AAPL \
  --start-date 2023-01-01 \
  --end-date 2024-01-01 \
  --amount 10000
```

#### Windows PowerShell (1行)
```powershell
python -m src.AAVC_calculate_tool backtest --ticker AAPL --start-date 2023-01-01 --end-date 2024-01-01 --amount 10000
```

#### Windows PowerShell (複数行)
```powershell
python -m src.AAVC_calculate_tool backtest `
  --ticker AAPL `
  --start-date 2023-01-01 `
  --end-date 2024-01-01 `
  --amount 10000
```

#### Windows Command Prompt (cmd.exe)
```cmd
python -m src.AAVC_calculate_tool backtest ^
  --ticker AAPL ^
  --start-date 2023-01-01 ^
  --end-date 2024-01-01 ^
  --amount 10000
```

**引数の説明:**
- `--ticker AAPL`: バックテスト対象の銘柄（例：AAPL、7203.T）
- `--start-date 2023-01-01`: バックテスト開始日
- `--end-date 2024-01-01`: バックテスト終了日
- `--amount 10000`: 基準投資額（円）

### 2. チャート付きバックテスト

#### Linux/macOS (bash)
```bash
python -m src.AAVC_calculate_tool backtest \
  --ticker AAPL \
  --start-date 2023-01-01 \
  --end-date 2024-01-01 \
  --amount 10000 \
  --plot
```

#### Windows PowerShell (1行)
```powershell
python -m src.AAVC_calculate_tool backtest --ticker AAPL --start-date 2023-01-01 --end-date 2024-01-01 --amount 10000 --plot
```

#### Windows PowerShell (複数行)
```powershell
python -m src.AAVC_calculate_tool backtest `
  --ticker AAPL `
  --start-date 2023-01-01 `
  --end-date 2024-01-01 `
  --amount 10000 `
  --plot
```

#### Windows Command Prompt (cmd.exe)
```cmd
python -m src.AAVC_calculate_tool backtest ^
  --ticker AAPL ^
  --start-date 2023-01-01 ^
  --end-date 2024-01-01 ^
  --amount 10000 ^
  --plot
```

`--plot` フラグを追加することで、比較チャートがPNGファイルとして保存されます。

## ⚙️ オプション設定

### 高度な設定例

#### Linux/macOS (bash)
```bash
python -m src.AAVC_calculate_tool backtest \
  --ticker 7203.T \
  --start-date 2022-01-01 \
  --end-date 2024-12-31 \
  --amount 50000 \
  --ref-price 1500 \
  --asymmetric-coefficient 1.2 \
  --volatility-period 30 \
  --plot
```

#### Windows PowerShell (1行)
```powershell
python -m src.AAVC_calculate_tool backtest --ticker 7203.T --start-date 2022-01-01 --end-date 2024-12-31 --amount 50000 --ref-price 1500 --asymmetric-coefficient 1.2 --volatility-period 30 --plot
```

#### Windows PowerShell (複数行)
```powershell
python -m src.AAVC_calculate_tool backtest `
  --ticker 7203.T `
  --start-date 2022-01-01 `
  --end-date 2024-12-31 `
  --amount 50000 `
  --ref-price 1500 `
  --asymmetric-coefficient 1.2 `
  --volatility-period 30 `
  --plot
```

#### Windows Command Prompt (cmd.exe)
```cmd
python -m src.AAVC_calculate_tool backtest ^
  --ticker 7203.T ^
  --start-date 2022-01-01 ^
  --end-date 2024-12-31 ^
  --amount 50000 ^
  --ref-price 1500 ^
  --asymmetric-coefficient 1.2 ^
  --volatility-period 30 ^
  --plot
```

**オプション引数の説明:**
- `--ref-price 1500`: 基準価格を1500円に設定
- `--asymmetric-coefficient 1.2`: AAVC戦略の非対称係数を1.2に設定
- `--volatility-period 30`: ボラティリティ計算期間を30日間に設定

## 📊 出力結果の見方

### 1. コンソール出力（サマリーテーブル）

```
## Backtest Result: AAPL (2023-01-01 to 2024-01-01)

| Metric(指標)     | AAVC         | DCA      | Buy & Hold |
|:-----------------|:-------------|:---------|:-----------|
| Final Value      | ¥4.3M       | ¥2.8M    | **¥5.9M**  |
| Ann. Return      | +14.8%      | +13.2%   | **+55.3%** |
| Total Return     | +14.7%      | +13.1%   | **+54.8%** |
| Max Drawdown     | +6.7%       | **+6.4%** | +14.9%     |
| Volatility(Ann.) | +157.4%     | +126.0%  | **+19.9%** |
| Sharpe Ratio     | 4.20        | **5.02** | 2.32       |
| Total Invested   | ¥3.8M       | ¥2.5M    | ¥3.8M      |
```

**指標の説明:**
- **Final Value**: 最終的なポートフォリオ価値
- **Ann. Return**: 年率収益率
- **Total Return**: 総収益率
- **Max Drawdown**: 最大下落率
- **Volatility(Ann.)**: 年率ボラティリティ
- **Sharpe Ratio**: シャープレシオ
- **Total Invested**: 総投資額

**太字の意味:**
各指標で最も優れた戦略が太字でハイライトされます。

### 2. チャート出力

`--plot` フラグを使用した場合、以下のファイルが生成されます：
- **ファイル名**: `backtest_chart_AAPL_2023-01-01_to_2024-01-01.png`
- **内容**: 3つの戦略の資産推移を1つのグラフに表示
- **色分け**: 
  - 青線: AAVC戦略
  - オレンジ線: DCA戦略
  - 緑線: Buy & Hold戦略

## 🎯 戦略の比較ポイント

### AAVC戦略
- **特徴**: 価格変動に応じて投資額を動的に調整
- **メリット**: 下落時に投資額を増加、上昇時に投資額を減少
- **デメリット**: 複雑な計算が必要

### DCA（ドルコスト平均法）
- **特徴**: 毎回同じ金額を投資
- **メリット**: シンプルで確実
- **デメリット**: 価格変動を活用できない

### Buy & Hold（一括投資）
- **特徴**: 初日に全額投資して保有
- **メリット**: 最もシンプル
- **デメリット**: タイミングのリスクが大きい

## 🔧 トラブルシューティング

### Windows環境での実行に関する注意事項

#### PowerShellでの複数行コマンド
PowerShellでは、バックスラッシュ（`\`）の代わりにバッククォート（`）を使用してください：

```powershell
# ❌ 間違い（PowerShellでは動作しません）
python -m src.AAVC_calculate_tool backtest \
  --ticker AAPL \
  --amount 10000

# ✅ 正しい（PowerShell用）
python -m src.AAVC_calculate_tool backtest `
  --ticker AAPL `
  --amount 10000
```

#### コマンドプロンプト（cmd.exe）での複数行コマンド
コマンドプロンプトでは、キャレット（`^`）を使用してください：

```cmd
# ✅ 正しい（cmd.exe用）
python -m src.AAVC_calculate_tool backtest ^
  --ticker AAPL ^
  --amount 10000
```

#### 推奨事項
Windows環境では、1行での実行を推奨します：

```powershell
# ✅ 推奨（Windows環境）
python -m src.AAVC_calculate_tool backtest --ticker AAPL --start-date 2023-01-01 --end-date 2024-01-01 --amount 10000
```

### よくあるエラーと対処法

#### 1. 必須引数が不足している場合
```
error: the following arguments are required: --start-date, --end-date, --amount
```
**対処法**: 不足している引数を追加してください。

#### 2. ティッカーが見つからない場合
```
Error: No data found for ticker 'INVALID' from 2023-01-01 to 2024-01-01
```
**対処法**: 正しいティッカーシンボルを指定してください。

#### 3. 日付形式が正しくない場合
```
Error: Invalid date format. Use YYYY-MM-DD
```
**対処法**: 日付を `YYYY-MM-DD` 形式で入力してください。

## 💡 使用のヒント

### 1. 適切な期間設定
- **短期**: 1-3ヶ月（短期トレンドの確認）
- **中期**: 6ヶ月-1年（戦略の有効性確認）
- **長期**: 1-3年（長期パフォーマンス評価）

### 2. 銘柄選択
- **米国株**: AAPL、GOOGL、MSFT など
- **日本株**: 7203.T（トヨタ）、6758.T（ソニー）など
- **ETF**: SPY、QQQ など

### 3. 投資額設定
- **小額**: 10,000円（テスト用）
- **中額**: 100,000円（実践的）
- **大額**: 1,000,000円（本格運用）

## 📈 結果の解釈

### 良い結果の例
- **AAVC戦略が他戦略を上回る**: 戦略が有効
- **Sharpe Ratio > 1.0**: リスク調整後収益が良好
- **Max Drawdown < 20%**: リスク管理が適切

### 注意が必要な結果
- **全戦略がマイナス収益**: 市場環境が悪い
- **Volatility > 50%**: リスクが高い
- **Max Drawdown > 30%**: 下落リスクが大きい

## 🔄 定期的な実行

### 月次バックテスト

#### Linux/macOS (bash)
```bash
# 毎月1日に実行
python -m src.AAVC_calculate_tool backtest \
  --ticker AAPL \
  --start-date $(date -d '1 month ago' +%Y-%m-01) \
  --end-date $(date +%Y-%m-%d) \
  --amount 10000 \
  --plot
```

#### Windows PowerShell
```powershell
# 毎月1日に実行（手動で日付を設定）
python -m src.AAVC_calculate_tool backtest --ticker AAPL --start-date 2024-01-01 --end-date 2024-02-01 --amount 10000 --plot
```

### 年次バックテスト

#### Linux/macOS (bash)
```bash
# 毎年1月1日に実行
python -m src.AAVC_calculate_tool backtest \
  --ticker AAPL \
  --start-date 2020-01-01 \
  --end-date 2024-01-01 \
  --amount 10000 \
  --plot
```

#### Windows PowerShell
```powershell
# 毎年1月1日に実行
python -m src.AAVC_calculate_tool backtest --ticker AAPL --start-date 2020-01-01 --end-date 2024-01-01 --amount 10000 --plot
```

## 📚 関連ドキュメント

- [要件定義書](05_Backtest_Comparison.md)
- [詳細設計書](05_Backtest_Comparison_Detailed_Design.md)
- [API リファレンス](API_Reference.md)

## 🆘 サポート

問題が発生した場合や質問がある場合は、以下を確認してください：

1. エラーメッセージの詳細
2. 使用したコマンドの完全な内容
3. 実行環境の詳細（OS、Python バージョンなど）
