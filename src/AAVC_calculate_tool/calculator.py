from datetime import date
from typing import Any, Dict, List

import numpy as np

from AAVC_calculate_tool.algorithm_registry import AlgorithmMetadata, BaseAlgorithm


class AAVCStrategy(BaseAlgorithm):
    """AAVC戦略のプラグイン化"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="aavc",
            description="Adaptive Asset Value Control Strategy",
            version="1.0",
            author="AAVC Team",
            parameters={
                "base_amount": {"type": "float", "default": 5000,
                                "description": "基準投資額"},
                "ref_price": {"type": "float", "default": None,
                              "description": "基準価格"},
                "asymmetric_coefficient": {"type": "float", "default": 2.0,
                                           "description": "非対称性係数"},
                "max_investment_multiplier": {"type": "float", "default": 3.0,
                                              "description": "最大投資額の基準額に対する倍率"},
                "investment_frequency": {"type": "str", "default": "monthly",
                                         "description": "投資頻度 (daily/monthly)"},
                "dynamic_ref_price_enabled": {"type": "bool", "default": True,
                                              "description": "動的基準価格を有効にするか"},
                "ref_price_reset_threshold": {"type": "float", "default": 2.0,
                                              "description": "基準価格をリセットするしきい値 (現在の価格が基準価格のX倍)"},
                "ref_price_reset_factor": {"type": "float", "default": 0.8,
                                           "description": "リセット時の新しい基準価格の係数 (現在の価格に対する割合)"},
            },
            category="value_averaging"
        )

    def __init__(self):
        super().__init__()
        self._current_effective_ref_price = None # Stores the dynamically adjusted reference price

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        base_amount = parameters.get("base_amount", 5000.0)
        ref_price_param = parameters.get("ref_price") # The initial fixed ref_price if provided
        asymmetric_coefficient = parameters.get("asymmetric_coefficient", 2.0)
        max_investment_multiplier = parameters.get("max_investment_multiplier", 3.0)
        investment_frequency = parameters.get("investment_frequency", "monthly")
        dynamic_ref_price_enabled = parameters.get("dynamic_ref_price_enabled", True)
        ref_price_reset_threshold = parameters.get("ref_price_reset_threshold", 2.0)
        ref_price_reset_factor = parameters.get("ref_price_reset_factor", 0.8)

        if not date_history:
            return 0.0

        current_date = date_history[-1]

        # Check if it's the investment day based on frequency
        if investment_frequency == "monthly":
            if len(date_history) > 1 and current_date.month == date_history[-2].month:
                return 0.0

        if not price_history:
            return 0.0

        # Determine the effective reference price
        effective_reference_price = 0.0

        if dynamic_ref_price_enabled:
            # Initialize _current_effective_ref_price on the first call
            if self._current_effective_ref_price is None:
                # Use the provided ref_price_param as the initial effective ref price
                # If ref_price_param is None, use the very first price in history
                self._current_effective_ref_price = ref_price_param if ref_price_param is not None else price_history[0]

            # Check for reset condition
            if current_price > self._current_effective_ref_price * ref_price_reset_threshold:
                old_ref_price = self._current_effective_ref_price
                self._current_effective_ref_price = current_price * ref_price_reset_factor
            
            effective_reference_price = self._current_effective_ref_price
        elif ref_price_param is not None: # Use fixed ref_price if provided and dynamic is not enabled
            effective_reference_price = ref_price_param
        elif price_history: # Fallback to first price in history
            effective_reference_price = price_history[0]
        
        # Use the determined effective_reference_price for AAVC logic
        reference_price = effective_reference_price

        # --- 2. ボラティリティの計算 ---
        if len(price_history) < 2:
            volatility = 0.0
        else:
            price_changes = np.abs(np.diff(price_history) / price_history[:-1])
            volatility = np.mean(price_changes)

        # --- 3. 乖離率の計算 ---
        if reference_price == 0:
            price_change_rate = 0.0
        else:
            price_change_rate = (reference_price - current_price) / reference_price

        # --- 4. 投資額調整率の計算 ---
        volatility_adjustment_factor = 1.0 + (volatility / 0.01)

        adjusted_rate = asymmetric_coefficient * price_change_rate * \
            volatility_adjustment_factor

        # --- 5. 最終投資額の計算 ---
        calculated_amount = base_amount * (1 + adjusted_rate)

        # --- 6. 投資額の制限 ---
        if calculated_amount < 0:
            return 0.0

        if calculated_amount > base_amount * max_investment_multiplier:
            return base_amount * max_investment_multiplier

        return float(calculated_amount)


class DCAStrategy(BaseAlgorithm):
    """DCA戦略のプラグイン化"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="dca",
            description="Dollar Cost Averaging Strategy",
            version="1.0",
            author="AAVC Team",
            parameters={
                "base_amount": {"type": "float", "default": 5000,
                                "description": "毎回の投資額"},
                "investment_frequency": {"type": "str", "default": "monthly",
                                         "description": "投資頻度 (daily/monthly)"},
            },
            category="systematic"
        )

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        base_amount = parameters.get("base_amount", 5000.0)
        investment_frequency = parameters.get("investment_frequency", "monthly")

        if not date_history: # 追加: date_historyが空の場合のチェック
            return 0.0

        current_date = date_history[-1]

        # Check if it's the investment day based on frequency
        if investment_frequency == "monthly":
            # Invest only on the first trading day of the month
            if len(date_history) > 1 and current_date.month == date_history[-2].month:
                return 0.0 # Not the first trading day of the month

        return base_amount


class BuyAndHoldStrategy(BaseAlgorithm):
    """Buy & Hold戦略のプラグイン化"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="buy_and_hold",
            description="Buy and Hold Strategy",
            version="1.0",
            author="AAVC Team",
            parameters={
                "initial_amount": {"type": "float", "default": 100000,
                                   "description": "初回投資額"}
            },
            category="passive"
        )

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        # Buy & Holdは初回のみ投資
        if len(price_history) == 1:  # 最初のデータポイントでのみ投資
            return parameters.get("initial_amount", 100000.0)
        return 0.0
