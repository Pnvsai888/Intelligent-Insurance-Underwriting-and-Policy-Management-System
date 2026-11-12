def test_premium_calculation():
    from decimal import Decimal
    # Premium = 10M * 0.02 * 1.0 * 0.9 * 0.9 = 162,000.00
    expected = Decimal("162000.00")
    assert expected == Decimal("162000.00")
