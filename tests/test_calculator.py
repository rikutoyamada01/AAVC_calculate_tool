import pytest

from src.AAVC_calculate_tool.calculator import calculate_aavc_investment


# Test cases for calculate_aavc_investment
def test_calculate_aavc_investment_basic_scenario():
    # Example from previous interactions: price increases, investment becomes 0
    price_path = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0, 116.0, 117.0, 118.0, 119.0, 120.0, 121.0, 122.0, 123.0, 124.0, 125.0, 126.0, 127.0, 128.0, 129.0, 130.0, 131.0, 132.0, 133.0, 134.0, 135.0, 136.0, 137.0, 138.0, 139.0, 140.0, 141.0, 142.0, 143.0, 144.0, 145.0, 146.0, 147.0, 148.0, 149.0, 150.0, 151.0, 152.0, 153.0, 154.0, 155.0, 156.0, 157.0, 158.0, 159.0]
    base_amount = 10000.0
    reference_price = 100.0 # Initial price

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount == 0.0 # Expect 0 because price has risen significantly

def test_calculate_aavc_investment_price_drop():
    # Scenario where price drops, should increase investment
    price_path = [100.0, 99.0, 98.0, 97.0, 96.0, 95.0, 94.0, 93.0, 92.0, 91.0, 90.0]
    base_amount = 10000.0
    reference_price = 100.0 # Initial price

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount > base_amount # Expect more than base amount
    assert calculated_amount == pytest.approx(14000.0, rel=0.01) # Expect around 14000, with 1% relative tolerance

def test_calculate_aavc_investment_no_price_change():
    # Scenario where price is same as reference, should be base_amount
    price_path = [100.0, 100.0, 100.0]
    base_amount = 10000.0
    reference_price = 100.0

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount == base_amount

def test_calculate_aavc_investment_negative_result_capped_at_zero():
    # Scenario where calculation would yield negative, but capped at 0
    price_path = [100.0, 150.0, 200.0] # Large price increase
    base_amount = 10000.0
    reference_price = 100.0

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount == 0.0

def test_calculate_aavc_investment_high_cap():
    # Scenario where calculation would exceed 3x base_amount, capped
    price_path = [100.0, 50.0, 20.0] # Large price drop
    base_amount = 10000.0
    reference_price = 100.0

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount == base_amount * 3 # Capped at 3x base_amount

def test_calculate_aavc_investment_empty_price_path():
    # Empty price path should return 0
    price_path = []
    base_amount = 10000.0
    reference_price = 100.0

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount == 0.0

def test_calculate_aavc_investment_single_price_path():
    # Single price in path, volatility should be 0
    price_path = [100.0]
    base_amount = 10000.0
    reference_price = 100.0

    calculated_amount = calculate_aavc_investment(price_path, base_amount, reference_price)
    assert calculated_amount == base_amount # No volatility, no price change from ref
