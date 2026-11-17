import pytest
from car_insurance_premium import annual_premium, no_claim_bonus, claim_payout

#Example test cases:
def test_sedan_no_claims():
    assert annual_premium("sedan", 30, 0, False) == 9600

def test_no_bonus():
    assert no_claim_bonus(0) == 0

#Write the rest of the test cases so that the code is 90- 100% covered.
