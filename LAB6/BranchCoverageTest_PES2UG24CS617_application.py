import pytest
from car_insurance_premium import annual_premium, no_claim_bonus, claim_payout


# ---------- annual_premium: car type branch ----------
@pytest.mark.parametrize("car,expected", [("hatchback", 6400), ("sedan", 9600), ("suv", 12000)])
def test_each_valid_car_type(car, expected):
    assert annual_premium(car, 30, 0, False) == expected


def test_unknown_car_type():
    with pytest.raises(ValueError, match="unknown car type"):
        annual_premium("bike", 30, 0, False)


# ---------- annual_premium: age branches (boundaries 18, 24/25, 59/60) ----------
def test_age_17_rejected():
    with pytest.raises(ValueError, match="driver too young"):
        annual_premium("sedan", 17, 1, False)


def test_age_18_accepted_young_loading():
    assert annual_premium("sedan", 18, 1, False) == 16000


def test_age_24_young_loading():
    assert annual_premium("sedan", 24, 1, False) == 16000


def test_age_25_no_loading():
    assert annual_premium("sedan", 25, 1, False) == 12000


def test_age_59_no_loading():
    assert annual_premium("sedan", 59, 1, False) == 12000


def test_age_60_senior_loading():
    assert annual_premium("sedan", 60, 1, False) == 14000


# ---------- annual_premium: claims branches (boundaries 0, 1, 2, 3) ----------
def test_zero_claims_discount():
    assert annual_premium("sedan", 30, 0, False) == 9600


def test_one_claim_no_change():
    assert annual_premium("sedan", 30, 1, False) == 12000


def test_two_claims_no_change():
    assert annual_premium("sedan", 30, 2, False) == 12000


def test_three_claims_doubled():
    assert annual_premium("sedan", 30, 3, False) == 24000


# ---------- annual_premium: anti-theft branch ----------
def test_anti_theft_true():
    assert annual_premium("sedan", 30, 1, True) == 11500


def test_anti_theft_false():
    assert annual_premium("sedan", 30, 1, False) == 12000


def test_combined_young_zero_claims_anti_theft():
    assert annual_premium("hatchback", 22, 0, True) == 9100


def test_combined_senior_many_claims_anti_theft():
    assert annual_premium("suv", 65, 3, True) == 33500


# ---------- no_claim_bonus ----------
def test_invalid_years():
    with pytest.raises(ValueError, match="invalid years"):
        no_claim_bonus(-1)


@pytest.mark.parametrize("years,expected", [
    (0, 0), (1, 20), (2, 20), (3, 35), (4, 35), (5, 50), (10, 50),
])
def test_no_claim_bonus_tiers(years, expected):
    assert no_claim_bonus(years) == expected


# ---------- claim_payout ----------
def test_negative_damage_rejected():
    with pytest.raises(ValueError, match="invalid amount"):
        claim_payout(-1, 10000, 500, False)


def test_negative_deductible_rejected():
    with pytest.raises(ValueError, match="invalid amount"):
        claim_payout(1000, 10000, -1, False)


def test_total_loss_pays_insured_value():
    assert claim_payout(50000, 40000, 1000, True) == 40000


def test_not_total_loss_flag_false_path():
    assert claim_payout(5000, 10000, 1000, False) == 4000


def test_damage_equal_to_deductible():
    assert claim_payout(1000, 10000, 1000, False) == 0


def test_damage_below_deductible():
    assert claim_payout(500, 10000, 1000, False) == 0


def test_payout_equal_to_insured_value():
    assert claim_payout(11000, 10000, 1000, False) == 10000


def test_payout_exceeds_insured_value():
    assert claim_payout(20000, 10000, 1000, False) == 10000


def test_zero_values():
    assert claim_payout(0, 0, 0, False) == 0
