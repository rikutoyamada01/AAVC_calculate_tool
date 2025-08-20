from datetime import date

import pytest

from src.AAVC_calculate_tool.calculator import AAVCStrategy


class TestAAVCStrategy:
    """Test cases for the AAVCStrategy class."""

    def setup_method(self):
        self.strategy = AAVCStrategy()
        self.base_params = {"base_amount": 10000.0, "asymmetric_coefficient": 2.0}

    def test_get_metadata(self):
        metadata = self.strategy.get_metadata()
        assert metadata.name == "aavc"
        assert "Adaptive Asset Value Control Strategy" in metadata.description
        assert "base_amount" in metadata.parameters

    def test_calculate_investment_price_increase(self):
        # Scenario where price increases, investment should decrease or be zero
        price_history = [100.0, 105.0, 110.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=110.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        # Expect investment to be 0 or very low as price has risen significantly
        assert calculated_amount <= self.base_params["base_amount"]
        assert calculated_amount >= 0.0

    def test_calculate_investment_price_drop(self):
        # Scenario where price drops, investment should increase
        price_history = [100.0, 95.0, 90.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=90.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount > self.base_params["base_amount"]
        # Check against a rough expected value (AAVC logic is complex, so approx)
        assert calculated_amount == pytest.approx(22263.157894736843)

    def test_calculate_investment_no_price_change(self):
        # Scenario where price is same as reference, should be base_amount
        price_history = [100.0, 100.0, 100.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=100.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == self.base_params["base_amount"]

    def test_calculate_investment_negative_result_capped_at_zero(self):
        # Scenario where calculation would yield negative, but capped at 0
        price_history = [100.0, 150.0, 200.0]  # Large price increase
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=200.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == 0.0

    def test_calculate_investment_high_cap(self):
        # Scenario where calculation would exceed 3x base_amount, capped
        price_history = [100.0, 50.0, 20.0]  # Large price drop
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=20.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == self.base_params["base_amount"] * 3  # Capped at 3x base_amount

    def test_calculate_investment_empty_price_path(self):
        # Empty price path should return 0
        price_history = []
        dates = []
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=100.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == 0.0

    def test_calculate_investment_single_price_path(self):
        # Single price in path, volatility should be 0
        price_history = [100.0]
        dates = [date(2023, 1, 1)]
        params = {**self.base_params, "reference_price": 100.0, "investment_frequency": "daily"}

        calculated_amount = self.strategy.calculate_investment(
            current_price=100.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == self.base_params["base_amount"]
