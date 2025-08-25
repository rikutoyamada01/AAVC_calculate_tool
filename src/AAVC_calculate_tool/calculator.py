from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict, List

import numpy as np

from AAVC_calculate_tool.algorithm_registry import AlgorithmMetadata, BaseAlgorithm

# --- AAVC Base Strategy ---

class BaseAAVCStrategy(BaseAlgorithm):
    """AAVC戦略の共通ロジックを定義する抽象基底クラス"""

    def __init__(self):
        super().__init__()
        # サブクラスで状態を管理する必要がある場合のために用意
        self._strategy_context: Dict[str, Any] = {}

    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        # サブクラスは自身のメタデータを定義する必要がある
        pass

    @abstractmethod
    def _calculate_reference_price(
        self,
        current_price: float,
        price_history: List[float],
        parameters: Dict[str, Any]
    ) -> float:
        # サブクラスは基準価格の計算方法を実装する必要がある
        pass

    def calculate_investment(
        self,
        current_price: float,
        price_history: List[float],
        date_history: List[date],
        parameters: Dict[str, Any]
    ) -> float:
        # --- 1. パラメータ取得と投資日判定 ---
        base_amount = parameters.get("base_amount", 5000.0)
        asymmetric_coefficient = parameters.get("asymmetric_coefficient", 2.0)
        max_investment_multiplier = parameters.get("max_investment_multiplier", 3.0)
        investment_frequency = parameters.get("investment_frequency", "monthly")

        if not date_history:
            return 0.0

        current_date = date_history[-1]
        if investment_frequency == "monthly":
            if len(date_history) > 1 and current_date.month == date_history[-2].month:
                return 0.0

        if not price_history:
            return 0.0

        # --- 2. 基準価格の計算 (サブクラスに委譲) ---
        reference_price = self._calculate_reference_price(
            current_price, price_history, parameters
        )

        # --- 3. ボラティリティの計算 ---
        if len(price_history) < 2:
            volatility = 0.0
        else:
            price_changes = np.abs(np.diff(price_history) / price_history[:-1])
            volatility = np.mean(price_changes)

        # --- 4. 乖離率の計算 ---
        if reference_price == 0:
            price_change_rate = 0.0
        else:
            price_change_rate = (reference_price - current_price) / reference_price

        # --- 5. 投資額調整率の計算 ---
        volatility_adjustment_factor = 1.0 + (volatility / 0.01)
        adjusted_rate = asymmetric_coefficient * price_change_rate * volatility_adjustment_factor

        # --- 6. 最終投資額の計算と制限 ---
        calculated_amount = base_amount * (1 + adjusted_rate)

        if calculated_amount < 0:
            return 0.0

        if calculated_amount > base_amount * max_investment_multiplier:
            return base_amount * max_investment_multiplier

        return float(calculated_amount)


# --- AAVC Strategy Implementations ---

class AAVCDynamicStrategy(BaseAAVCStrategy):
    """バージョン2: 価格上昇時に基準価格を動的にリセットする戦略"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="aavc_dynamic",
            description="AAVC with Dynamic Reference Price Reset Strategy",
            version="2.0",
            author="AAVC Team",
            parameters={
                "base_amount": {"type": "float", "default": 5000, "description": "基準投資額"},
                "ref_price": {"type": "float", "default": None, "description": "初期基準価格"},
                "asymmetric_coefficient": {"type": "float", "default": 2.0, "description": "非対称性係数"},
                "max_investment_multiplier": {"type": "float", "default": 3.0, "description": "最大投資額の基準額に対する倍率"},
                "investment_frequency": {"type": "str", "default": "monthly", "description": "投資頻度 (daily/monthly)"},
                "ref_price_reset_threshold": {"type": "float", "default": 2.0, "description": "基準価格をリセットするしきい値"},
                "ref_price_reset_factor": {"type": "float", "default": 0.8, "description": "リセット時の新しい基準価格の係数"},
            },
            category="value_averaging"
        )

    def _calculate_reference_price(
        self,
        current_price: float,
        price_history: List[float],
        parameters: Dict[str, Any]
    ) -> float:
        ref_price_param = parameters.get("ref_price")
        ref_price_reset_threshold = parameters.get("ref_price_reset_threshold", 2.0)
        ref_price_reset_factor = parameters.get("ref_price_reset_factor", 0.8)

        current_effective_ref_price = self._strategy_context.get("_current_effective_ref_price")

        if current_effective_ref_price is None:
            current_effective_ref_price = ref_price_param if ref_price_param is not None else price_history[0]

        if current_price > current_effective_ref_price * ref_price_reset_threshold:
            current_effective_ref_price = current_price * ref_price_reset_factor
        
        self._strategy_context["_current_effective_ref_price"] = current_effective_ref_price
        return current_effective_ref_price

class AAVCStaticStrategy(BaseAAVCStrategy):
    """バージョン1: 固定または初期価格を基準とする戦略"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="aavc_static",
            description="AAVC with Static Reference Price Strategy",
            version="1.0",
            author="AAVC Team",
            parameters={
                "base_amount": {"type": "float", "default": 5000, "description": "基準投資額"},
                "ref_price": {"type": "float", "default": None, "description": "固定基準価格 (指定なければ初期価格)"},
                "asymmetric_coefficient": {"type": "float", "default": 2.0, "description": "非対称性係数"},
                "max_investment_multiplier": {"type": "float", "default": 3.0, "description": "最大投資額の基準額に対する倍率"},
                "investment_frequency": {"type": "str", "default": "monthly", "description": "投資頻度 (daily/monthly)"},
            },
            category="value_averaging"
        )

    def _calculate_reference_price(
        self,
        current_price: float,
        price_history: List[float],
        parameters: Dict[str, Any]
    ) -> float:
        ref_price_param = parameters.get("ref_price")
        if ref_price_param is not None:
            return ref_price_param
        return price_history[0] if price_history else 0.0

class AAVCMovingAverageStrategy(BaseAAVCStrategy):
    """バージョン3: 移動平均線を基準価格とする戦略"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="aavc_ma",
            description="AAVC with Moving Average Reference Price Strategy",
            version="1.0",
            author="AAVC Team",
            parameters={
                "base_amount": {"type": "float", "default": 5000, "description": "基準投資額"},
                "asymmetric_coefficient": {"type": "float", "default": 2.0, "description": "非対称性係数"},
                "max_investment_multiplier": {"type": "float", "default": 3.0, "description": "最大投資額の基準額に対する倍率"},
                "investment_frequency": {"type": "str", "default": "monthly", "description": "投資頻度 (daily/monthly)"},
                "window_size": {"type": "int", "default": 200, "description": "移動平均の計算期間（日数）"},
            },
            category="value_averaging"
        )

    def _calculate_reference_price(
        self,
        current_price: float,
        price_history: List[float],
        parameters: Dict[str, Any]
    ) -> float:
        window_size = parameters.get("window_size", 200)
        if len(price_history) < window_size:
            return price_history[0] # データが足りない場合は初期価格
        
        return np.mean(price_history[-window_size:])


class AAVCHighestPriceResetStrategy(BaseAAVCStrategy):
    """最高値更新時に基準価格をリセットする戦略"""

    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="aavc_highest_reset",
            description="AAVC with Reference Price Reset on New Highest Price",
            version="1.0",
            author="AAVC Team",
            parameters={
                "base_amount": {"type": "float", "default": 5000, "description": "基準投資額"},
                "asymmetric_coefficient": {"type": "float", "default": 2.0, "description": "非対称性係数"},
                "max_investment_multiplier": {"type": "float", "default": 3.0, "description": "最大投資額の基準額に対する倍率"},
                "investment_frequency": {"type": "str", "default": "monthly", "description": "投資頻度 (daily/monthly)"},
                "reset_factor": {"type": "float", "default": 0.80, "description": "基準価格リセット係数 (最高値 * N)"},
            },
            category="value_averaging"
        )

    def _calculate_reference_price(
        self,
        current_price: float,
        price_history: List[float],
        parameters: Dict[str, Any]
    ) -> float:
        reset_factor = parameters.get("reset_factor", 0.85)

        # Initialize highest_price_seen in strategy context if not present
        if "_highest_price_seen" not in self._strategy_context:
            self._strategy_context["_highest_price_seen"] = price_history[0] if price_history else 0.0
            # Also initialize the effective reference price to the first price
            self._strategy_context["_current_effective_ref_price"] = (price_history[0] * reset_factor) if price_history else 0.0

        highest_price_seen = self._strategy_context["_highest_price_seen"]
        current_effective_ref_price = self._strategy_context["_current_effective_ref_price"]

        # Update highest_price_seen
        if current_price > highest_price_seen:
            highest_price_seen = current_price
            self._strategy_context["_highest_price_seen"] = highest_price_seen
            
            # Reset reference price based on new highest price
            current_effective_ref_price = highest_price_seen * reset_factor
            self._strategy_context["_current_effective_ref_price"] = current_effective_ref_price
        
        return current_effective_ref_price


# --- Other Strategies (Unchanged) ---

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