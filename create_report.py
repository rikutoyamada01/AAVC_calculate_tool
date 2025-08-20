import os

def generate_markdown_table(result):
    """ComparisonResultオブジェクトから手動でマークダウンのテーブルを生成する"""
    header = ["戦略", "最終評価額", "総投資額", "リターン率", "年率リターン", "最大下落率", "シャープレシオ"]
    
    # データを文字列のリストとして準備
    rows = []
    sorted_algorithms = sorted(result.results.keys(), key=lambda k: result.results[k].total_return, reverse=True)
    for name in sorted_algorithms:
        res = result.results[name]
        rows.append([
            name.upper(),
            f"{res.final_value:,.0f}円",
            f"{res.total_invested:,.0f}円",
            f"**{res.total_return:.2f}%**",
            f"{res.annual_return:.2f}%",
            f"{res.max_drawdown:.2f}%",
            f"{res.sharpe_ratio:.2f}",
        ])

    # 各列の最大幅を計算
    col_widths = [len(h) for h in header]
    for row in rows:
        for i, cell in enumerate(row):
            if len(cell) > col_widths[i]:
                col_widths[i] = len(cell)

    # テーブル文字列を生成
    # ヘッダー
    header_line = "| " + " | ".join([h.ljust(w) for h, w in zip(header, col_widths)]) + " |"
    # 区切り線 (アラインメント指定)
    separator_parts = []
    for i, h in enumerate(header):
        # 戦略列は左寄せ、他は右寄せ
        if h == "戦略":
            separator_parts.append(":" + "-" * (col_widths[i] - 1))
        else:
            separator_parts.append("-" * (col_widths[i] - 1) + ":")
    separator_line = "| " + " | ".join(separator_parts) + " |"
    
    # データ行
    data_lines = []
    for row in rows:
        formatted_row = []
        for i, cell in enumerate(row):
            # 戦略列は左寄せ、他は右寄せ
            if header[i] == "戦略":
                formatted_row.append(cell.ljust(col_widths[i]))
            else:
                formatted_row.append(cell.rjust(col_widths[i]))
        data_lines.append("| " + " | ".join(formatted_row) + " |")

    return "\n".join([header_line, separator_line] + data_lines)

from AAVC_calculate_tool.backtester import run_comparison_backtest
from AAVC_calculate_tool.plotter import plot_multi_algorithm_chart


def create_report_section(ticker, start_date, end_date, base_params, title, description):
    """単一の市場局面のレポートセクションを生成する"""
    print(f"Running simulation for: {title} ({start_date} to {end_date})...")
    try:
        # 1. バックテスト実行
        comparison_result = run_comparison_backtest(
            ticker=ticker,
            start_date_str=start_date,
            end_date_str=end_date,
            base_parameters=base_params,
            algorithm_names=["aavc", "dca"]
        )

        # 2. チャート生成
        # chartsディレクトリがなければ作成
        if not os.path.exists("charts"):
            os.makedirs("charts")
        chart_filename = f"charts/{ticker}_{title.replace(' ', '_')}.png"
        plot_multi_algorithm_chart(comparison_result, output_filename=chart_filename)

        # 3. パフォーマンス表生成
        markdown_table = generate_markdown_table(comparison_result)

        # 4. マークダウンセクション生成
        section = f"## {title}\n\n"
        section += f"{description}\n\n"
        section += f"**期間:** {start_date} 〜 {end_date}\n"
        section += f"**対象銘柄:** {ticker}\n\n"
        section += "### パフォーマンス比較\n\n"
        section += markdown_table + "\n\n"
        section += "### 資産推移チャート\n\n"
        section += f"![{title}]({chart_filename})\n\n"
        
        # 5. 簡単な考察を追加
        aavc_return = comparison_result.results['aavc'].total_return
        dca_return = comparison_result.results['dca'].total_return
        aavc_mdd = comparison_result.results['aavc'].max_drawdown
        dca_mdd = comparison_result.results['dca'].max_drawdown
        max_monthly_investment = max(comparison_result.results['aavc'].investment_history)
        base_amount = comparison_result.results['aavc'].metadata.get('base_amount', 1) # ゼロ除算を避ける
        max_investment_ratio = max_monthly_investment / base_amount if base_amount else 0

        section += "### 考察\n"
        if aavc_return > dca_return:
            section += f"この局面では、AAVCがDCAを **{aavc_return - dca_return:.2f}ポイント** 上回るリターンを達成しました。"
            if aavc_mdd < dca_mdd:
                section += f"また、最大下落率も小さく抑えられており、下落局面で安く買い増しができたことが、後のリターン向上に繋がったと考えられます。\n\n"
            else:
                section += f"一方で、最大下落率はDCAを上回っており、より積極的に買い向かった結果、一時的な含み損は大きくなる局面もありました。\n\n"
        else:
            section += f"この局面では、DCAがAAVCを **{dca_return - aavc_return:.2f}ポイント** 上回るリターンを達成しました。"
            section += f"これは、価格が大きく下がることなく上昇を続けたため、積極的に買い増す機会が少なく、機会損失となった可能性が考えられます。\n\n"
        
        section += f"ちなみに、この局面でAAVCが1ヶ月に投資した最大額は **{max_monthly_investment:,.0f}円** であり、これは基準投資額（{base_amount:,.0f}円）の **{max_investment_ratio:.2f}倍** に相当します。\n\n"

        return section

    except Exception as e:
        print(f"Error during simulation for {title}: {e}")
        return f"## {title}\n\nシミュレーション中にエラーが発生しました: {e}\n\n"

def main():
    """メイン関数"""
    report = "# AAVC vs DCA パフォーマンス比較レポート (QQQ)\n\n"
    report += "本レポートは、AAVC戦略とDCA（ドルコスト平均法）戦略のパフォーマンスを、様々な市場局面で比較検証したものです。\n\n"

    base_parameters = {
        "base_amount": 30000, # 毎月の基準投資額を3万円に設定
        "aavc": {
            "asymmetric_coefficient": 2.0,
            "max_investment_multiplier": 3.0,
        }
    }
    
    # --- 各局面のシミュレーション ---
    scenarios = [
        {"title": "V字回復・上昇相場", "start": "2020-01-01", "end": "2021-12-31", "desc": "コロナショックによる暴落と、その後の金融緩和による急激な回復・上昇局面です。"},
        {"title": "下落相場", "start": "2022-01-01", "end": "2022-12-31", "desc": "世界的な金融引き締めを背景とした、一貫した下落局面です。"},
        {"title": "レンジ相場", "start": "2015-01-01", "end": "2016-12-31", "desc": "大きなトレンドがなく、一定の範囲で価格が上下する横ばい局面です。"},
        {"title": "総集編・長期シミュレーション", "start": "2015-01-01", "end": "2022-12-31", "desc": "これまで分析したレンジ、上昇、下落のすべての局面を含む、約8年間の長期的なパフォーマンスを検証します。"}
    ]

    for s in scenarios:
        report += create_report_section(
            ticker="QQQ", 
            start_date=s["start"],
            end_date=s["end"],
            base_params=base_parameters, 
            title=s["title"], 
            description=s["desc"]
        )
        report += "---\n\n" # セクション区切り

    # --- レポートファイル書き出し ---
    report_filename = "AAVC_vs_DCA_report_QQQ.md"
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"レポートが正常に生成されました: {report_filename}")

if __name__ == "__main__":
    main()
