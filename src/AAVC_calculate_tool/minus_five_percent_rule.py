from datetime import date, timedelta
from typing import Any, Dict, List

from AAVC_calculate_tool.algorithm_registry import AlgorithmMetadata, BaseAlgorithm


class MinusFivePercentRuleStrategy(BaseAlgorithm):
    """
    -5%ルール戦略: 前月の最終取引日の終値から今月の最終取引日の終値が指定パーセント下落した場合に一括購入
    """

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="minus_five_percent_rule",
            description="Buy a lump sum when price drops by a percentage from previous month's close.",
            version="1.2", # バージョンを更新
            author="Gemini",
            parameters={
                "base_amount": {"type": "float", "default": 10000.0,
                                "description": "一括購入する金額"},
                "drop_percentage": {"type": "float", "default": 0.05,
                                    "description": "下落率の閾値 (例: 0.05で5%)"},
                "investment_frequency": {"type": "str", "default": "monthly",
                                         "description": "チェック頻度 (daily/monthly)"},
            },
            category="event_driven"
        )

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        base_amount = parameters.get("base_amount", 10000.0)
        drop_percentage = parameters.get("drop_percentage", 0.05)
        investment_frequency = parameters.get("investment_frequency", "monthly")

        if len(price_history) < 2:
            return 0.0  # 比較するデータがない場合は投資しない

        current_date = date_history[-1]
        current_date_index = len(date_history) - 1 # current_dateのインデックス

        # Determine if it's the check day based on frequency
        is_check_day = False
        if investment_frequency == "daily":
            is_check_day = True
        elif investment_frequency == "monthly":
            # 今月の最終取引日をチェック
            # current_dateがdate_historyの最後の要素である場合、
            # または次の日の月が現在の月と異なる場合
            if current_date_index == len(date_history) - 1: # データセットの最終日
                is_check_day = True
            elif (current_date_index + 1 < len(date_history)) and \
                 (date_history[current_date_index + 1].month != current_date.month):
                is_check_day = True

        if not is_check_day:
            return 0.0 # Not the check day, skip

        previous_month_close_price = None
        
        # 前月の最終取引日の終値を探す
        # current_dateの月が始まる前の日付の中で、最も新しい日付の価格を探す
        # current_date_indexから逆順に辿り、current_dateの月と異なる最初の月の最終日を探す
        for i in range(current_date_index - 1, -1, -1):
            prev_date = date_history[i]
            if prev_date.month != current_date.month:
                # prev_dateが前月の最終取引日であると仮定し、その価格を取得
                previous_month_close_price = price_history[i]
                break # 見つかったのでループを抜ける
        
        if previous_month_close_price is None:
            return 0.0

        # 下落率の条件をチェック
        if previous_month_close_price > 0 and \
           (previous_month_close_price - current_price) / previous_month_close_price >= drop_percentage:
            return base_amount
        else:
            return 0.0