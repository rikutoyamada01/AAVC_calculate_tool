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
                "reference_price_ma_factor": {"type": "float", "default": 1.0,
                                              "description": "移動平均基準価格に乗算する係数"},
                "reference_price_ma_period": {"type": "int", "default": 200,
                                              "description": "基準価格として使用する移動平均の期間"},
            },
            category="value_averaging"
        )

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        base_amount = parameters.get("base_amount", 5000.0)
        reference_price = parameters.get("ref_price")
        asymmetric_coefficient = parameters.get("asymmetric_coefficient", 2.0)
        max_investment_multiplier = parameters.get("max_investment_multiplier", 3.0)
        reference_price_ma_factor = parameters.get("reference_price_ma_factor", 1.0)
        reference_price_ma_period = parameters.get("reference_price_ma_period", 200)

        # --- 1. 株価の確認 ---
        if not price_history:
            return 0.0  # 株価データがない場合は0を返す

        # 動的な基準価格の計算
        if reference_price is not None: # Fixed ref_price takes precedence
            calculated_reference_price = reference_price
        elif len(price_history) >= reference_price_ma_period:
            # 移動平均を計算
            ma_prices = price_history[-reference_price_ma_period:]
            calculated_reference_price = np.mean(ma_prices) * reference_price_ma_factor
        # それも不可能であれば、その他のフォールバックロジック
        elif price_history: # Fallback to first price in history if no fixed ref price
            calculated_reference_price = price_history[0]
        else: # Fallback to current price if no history and no fixed ref price
            calculated_reference_price = current_price

        # Use the calculated_reference_price as the actual reference_price for AAVC logic
        reference_price = calculated_reference_price

        # --- 2. ボラティリティの計算 ---
        if len(price_history) < 2:
            volatility = 0.0
        else:
            # 価格の変動率を計算
            price_changes = np.abs(np.diff(price_history) / price_history[:-1])
            volatility = np.mean(price_changes)

        # --- 3. 乖離率の計算 ---
        if reference_price == 0:
            price_change_rate = 0.0
        else:
            price_change_rate = (reference_price - current_price) / reference_price

        # --- 4. 投資額調整率の計算 ---
        # ボラティリティ調整係数を計算
        volatility_adjustment_factor = 1.0 + (volatility / 0.01)  # 基準ボラティリティは1%に設定

        adjusted_rate = asymmetric_coefficient * price_change_rate * \
            volatility_adjustment_factor

        # --- 5. 最終投資額の計算 ---
        calculated_amount = base_amount * (1 + adjusted_rate)

        # --- 6. 投資額の制限 ---
        # 投資額がマイナスにならないように
        if calculated_amount < 0:
            return 0.0

        # 上限キャップ
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
                                "description": "毎回の投資額"}
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
        return parameters.get("base_amount", 5000.0)


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
