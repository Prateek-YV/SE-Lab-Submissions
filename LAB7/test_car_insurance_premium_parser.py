from hypothesis import given, strategies as st
from car_insurance_premium_parser import normalize_registration, total_claim_amount, driver_age


# ---------------------------------------------------------------------------
# 1. "No crash" fuzz tests (one per function)
#    Inputs: random Unicode text OR None
# ---------------------------------------------------------------------------

@given(st.text() | st.none())
def test_normalize_registration_no_crash(s):
    try:
        normalize_registration(s)
    except Exception as e:
        assert False, f"normalize_registration crashed with: {e!r} on input {s!r}"


@given(st.text() | st.none())
def test_total_claim_amount_no_crash(s):
    try:
        total_claim_amount(s)
    except Exception as e:
        assert False, f"total_claim_amount crashed with: {e!r} on input {s!r}"


@given(st.text() | st.none())
def test_driver_age_no_crash(s):
    try:
        driver_age(s)
    except Exception as e:
        assert False, f"driver_age crashed with: {e!r} on input {s!r}"


# ---------------------------------------------------------------------------
# 2. Extra property checks: the functions must not just survive, they must
#    return sensible values. These also pass on the fixed module.
# ---------------------------------------------------------------------------

@given(st.text() | st.none())
def test_normalize_registration_output_is_clean(s):
    result = normalize_registration(s)
    assert isinstance(result, str)
    assert result == result.upper()
    assert not any(ch.isspace() or ch in "-." for ch in result)


@given(st.lists(st.integers(min_value=0, max_value=10**9), max_size=20))
def test_total_claim_amount_matches_sum_for_valid_input(amounts):
    text = ";".join(str(a) for a in amounts)
    assert total_claim_amount(text) == sum(amounts)


@given(st.text() | st.none())
def test_total_claim_amount_never_negative(s):
    result = total_claim_amount(s)
    assert isinstance(result, int)
    assert result >= 0


@given(
    st.integers(min_value=1, max_value=28),
    st.integers(min_value=1, max_value=12),
    st.integers(min_value=1950, max_value=2026),
)
def test_driver_age_valid_dates(day, month, year):
    dob = f"{day:02d}/{month:02d}/{year}"
    assert driver_age(dob) == 2026 - year


@given(st.text() | st.none())
def test_driver_age_result_is_none_or_sane_int(s):
    result = driver_age(s)
    assert result is None or (isinstance(result, int) and 0 <= result <= 150)
