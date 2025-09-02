from datetime import date

import pytest

from src.AAVC_calculate_tool.calculator import AAVCStaticStrategy, AAVCHighestPriceResetStrategy, AAVCHighestInHistoryStrategy


class TestAAVCStaticStrategy:
    """Test cases for the AAVCStaticStrategy class."""

    def setup_method(self):
        self.strategy = AAVCStaticStrategy()
        self.base_params = {
            "base_amount": 10000.0,
            "asymmetric_coefficient": 2.0,
            "max_investment_multiplier": 3.0,
            "investment_frequency": "daily" # Daily for easier testing
        }

    def test_get_metadata(self):
        metadata = self.strategy.get_metadata()
        assert metadata.name == "aavc_static"
        assert "AAVC with Static Reference Price Strategy" in metadata.description
        assert "base_amount" in metadata.parameters
        assert "ref_price" in metadata.parameters

    def test_calculate_investment_price_increase(self):
        # Scenario where price increases, investment should decrease or be zero
        price_history = [100.0, 105.0, 110.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "ref_price": 100.0}

        calculated_amount = self.strategy.calculate_investment(
            current_price=110.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount < self.base_params["base_amount"]
        assert calculated_amount >= 0.0

    def test_calculate_investment_price_drop(self):
        # Scenario where price drops, investment should increase
        price_history = [100.0, 95.0, 90.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "ref_price": 100.0}

        calculated_amount = self.strategy.calculate_investment(
            current_price=90.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount > self.base_params["base_amount"]

    def test_calculate_investment_no_price_change(self):
        # Scenario where price is same as reference, should be base_amount
        price_history = [100.0, 100.0, 100.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "ref_price": 100.0}

        calculated_amount = self.strategy.calculate_investment(
            current_price=100.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == self.base_params["base_amount"]

    def test_calculate_investment_negative_result_capped_at_zero(self):
        # Scenario where calculation would yield negative, but capped at 0
        price_history = [100.0, 150.0, 200.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "ref_price": 100.0}

        calculated_amount = self.strategy.calculate_investment(
            current_price=200.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == 0.0

    def test_calculate_investment_high_cap(self):
        # Scenario where calculation would exceed max_investment_multiplier
        price_history = [100.0, 50.0, 20.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params, "ref_price": 100.0}

        calculated_amount = self.strategy.calculate_investment(
            current_price=20.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == self.base_params["base_amount"] * self.base_params["max_investment_multiplier"]

    def test_calculate_investment_empty_price_path(self):
        # Empty price path should return 0
        price_history = []
        dates = []
        params = {**self.base_params, "ref_price": 100.0}

        calculated_amount = self.strategy.calculate_investment(
            current_price=100.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        assert calculated_amount == 0.0

    def test_calculate_investment_no_ref_price_uses_first_price(self):
        # If no ref_price is provided, it should use the first price in history
        price_history = [95.0, 100.0, 105.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params} # No ref_price

        calculated_amount = self.strategy.calculate_investment(
            current_price=105.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        # Reference price becomes 95.0, current is 105.0, so investment should be low/zero
        assert calculated_amount < self.base_params["base_amount"]
        assert calculated_amount >= 0.0


class TestAAVCHighestPriceResetStrategy:
    """Test cases for the AAVCHighestPriceResetStrategy class."""

    def setup_method(self):
        self.strategy = AAVCHighestPriceResetStrategy()
        self.base_params = {
            "base_amount": 10000.0,
            "asymmetric_coefficient": 2.0,
            "max_investment_multiplier": 3.0,
            "investment_frequency": "daily",
            "reset_factor": 0.85
        }

    def test_get_metadata(self):
        metadata = self.strategy.get_metadata()
        assert metadata.name == "aavc_highest_reset"
        assert "AAVC with Reference Price Reset on New Highest Price" in metadata.description
        assert "reset_factor" in metadata.parameters

    def test_calculate_reference_price_initial(self):
        # Initial state, reference price should be first price * reset_factor
        price_history = [100.0]
        params = {**self.base_params}
        ref_price = self.strategy._calculate_reference_price(
            current_price=100.0, price_history=price_history, parameters=params
        )
        assert ref_price == 100.0 * 0.85
        assert self.strategy._strategy_context["_highest_price_seen"] == 100.0
        assert self.strategy._strategy_context["_current_effective_ref_price"] == 100.0 * 0.85

    def test_calculate_reference_price_new_high(self):
        # New high, reference price should reset
        price_history = [100.0, 105.0, 110.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params}

        # Simulate initial call
        self.strategy._calculate_reference_price(
            current_price=100.0, price_history=[100.0], parameters=params
        )
        # Simulate new high
        ref_price = self.strategy._calculate_reference_price(
            current_price=110.0, price_history=price_history, parameters=params
        )
        assert ref_price == 110.0 * 0.85
        assert self.strategy._strategy_context["_highest_price_seen"] == 110.0
        assert self.strategy._strategy_context["_current_effective_ref_price"] == 110.0 * 0.85

    def test_calculate_reference_price_no_new_high(self):
        # No new high, reference price should remain the same
        price_history = [100.0, 90.0, 80.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params}

        # Simulate initial call
        self.strategy._calculate_reference_price(
            current_price=100.0, price_history=[100.0], parameters=params
        )
        # Simulate no new high
        ref_price = self.strategy._calculate_reference_price(
            current_price=90.0, price_history=price_history, parameters=params
        )
        assert ref_price == 100.0 * 0.85 # Should still be based on initial high
        assert self.strategy._strategy_context["_highest_price_seen"] == 100.0
        assert self.strategy._strategy_context["_current_effective_ref_price"] == 100.0 * 0.85

    def test_calculate_investment_new_high_reset(self):
        # Test investment calculation with new high and reset
        price_history = [100.0, 105.0, 110.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params}

        # Simulate initial call to set context
        self.strategy._calculate_reference_price(
            current_price=100.0, price_history=[100.0], parameters=params
        )

        # Calculate investment after new high
        calculated_amount = self.strategy.calculate_investment(
            current_price=110.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        # Expect investment to be lower than base_amount as price is above new reference
        assert calculated_amount < self.base_params["base_amount"]
        assert calculated_amount >= 0.0

    def test_calculate_investment_no_new_high(self):
        # Test investment calculation with no new high
        price_history = [100.0, 90.0, 80.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params}

        # Simulate initial call to set context
        self.strategy._calculate_reference_price(
            current_price=100.0, price_history=[100.0], parameters=params
        )

        # Calculate investment with no new high
        calculated_amount = self.strategy.calculate_investment(
            current_price=80.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        # Expect investment to be higher than base_amount as price is below reference
        assert calculated_amount > self.base_params["base_amount"]


class TestAAVCHighestInHistoryStrategy:
    """Test cases for the AAVCHighestInHistoryStrategy class."""

    def setup_method(self):
        self.strategy = AAVCHighestInHistoryStrategy()
        self.base_params = {
            "base_amount": 10000.0,
            "asymmetric_coefficient": 2.0,
            "max_investment_multiplier": 3.0,
            "investment_frequency": "daily",
            "reset_factor": 0.85
        }

    def test_get_metadata(self):
        metadata = self.strategy.get_metadata()
        assert metadata.name == "aavc_highest_in_history"
        assert "AAVC with Reference Price based on Highest Price in Current History" in metadata.description
        assert "reset_factor" in metadata.parameters

    def test_calculate_reference_price_basic(self):
        # Test with a simple history where max is at the end
        price_history = [100.0, 105.0, 110.0]
        params = {**self.base_params}
        ref_price = self.strategy._calculate_reference_price(
            current_price=110.0, price_history=price_history, parameters=params
        )
        assert ref_price == 110.0 * 0.85

    def test_calculate_reference_price_max_in_middle(self):
        # Test with max price in the middle of history
        price_history = [100.0, 120.0, 110.0]
        params = {**self.base_params}
        ref_price = self.strategy._calculate_reference_price(
            current_price=110.0, price_history=price_history, parameters=params
        )
        assert ref_price == 120.0 * 0.85

    def test_calculate_reference_price_max_at_start(self):
        # Test with max price at the start of history
        price_history = [130.0, 110.0, 100.0]
        params = {**self.base_params}
        ref_price = self.strategy._calculate_reference_price(
            current_price=100.0, price_history=price_history, parameters=params
        )
        assert ref_price == 130.0 * 0.85

    def test_calculate_reference_price_empty_history(self):
        # Test with empty history
        price_history = []
        params = {**self.base_params}
        ref_price = self.strategy._calculate_reference_price(
            current_price=0.0, price_history=price_history, parameters=params
        )
        assert ref_price == 0.0

    def test_calculate_investment_basic(self):
        # Test a full investment calculation
        price_history = [100.0, 105.0, 110.0]
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        params = {**self.base_params}

        calculated_amount = self.strategy.calculate_investment(
            current_price=110.0, price_history=price_history, date_history=dates,
            parameters=params
        )
        # Expected reference price: 110.0 * 0.85 = 93.5
        # Current price: 110.0. Price is above reference, so investment should be low/zero
        assert calculated_amount < self.base_params["base_amount"]
        assert calculated_amount >= 0.0
