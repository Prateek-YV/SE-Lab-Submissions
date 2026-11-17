import pytest
from car_insurance_premium import annual_premium, no_claim_bonus, claim_payout


# ---------- annual_premium ----------
def test_sedan_no_claims():
    assert annual_premium("sedan", 30, 0, False) == 9600


def test_unknown_car_type():
    with pytest.raises(ValueError, match="unknown car type"):
        annual_premium("bike", 30, 0, False)


def test_driver_too_young():
    with pytest.raises(ValueError, match="driver too young"):
        annual_premium("sedan", 17, 0, False)


def test_young_driver_no_claims_anti_theft():
    # 8000 + 4000 = 12000 -> -2400 = 9600 -> -500 = 9100
    assert annual_premium("hatchback", 22, 0, True) == 9100


def test_senior_driver_many_claims():
    # 15000 + 2000 = 17000 -> x2 = 34000
    assert annual_premium("suv", 65, 3, False) == 34000


# ---------- no_claim_bonus ----------
def test_no_bonus():
    assert no_claim_bonus(0) == 0


def test_invalid_years():
    with pytest.raises(ValueError, match="invalid years"):
        no_claim_bonus(-1)


def test_bonus_five_years():
    assert no_claim_bonus(5) == 50


def test_bonus_three_years():
    assert no_claim_bonus(3) == 35


def test_bonus_one_year():
    assert no_claim_bonus(1) == 20


# ---------- claim_payout ----------
def test_invalid_amount():
    with pytest.raises(ValueError, match="invalid amount"):
        claim_payout(-100, 10000, 500, False)


def test_total_loss():
    assert claim_payout(50000, 40000, 1000, True) == 40000


def test_damage_below_deductible():
    assert claim_payout(500, 10000, 1000, False) == 0


def test_payout_capped_at_insured_value():
    assert claim_payout(20000, 10000, 1000, False) == 10000


def test_normal_payout():
    assert claim_payout(5000, 10000, 1000, False) == 4000
