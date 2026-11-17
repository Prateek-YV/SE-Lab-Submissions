import datetime


def normalize_registration(plate):
    """
    Removes whitespace, dashes and dots from a registration number and
    upper-cases it.

    Never raises: anything that is not a string (None, numbers, ...) gives "".
    """
    if not isinstance(plate, str):
        return ""
    cleaned = "".join(ch for ch in plate if not ch.isspace() and ch not in "-.")
    return cleaned.upper()


def total_claim_amount(text):
    """
    Adds up claim amounts separated by semicolons.

    Never raises. Blank entries ("12;;5"), non-numeric entries, negative
    numbers, decimals and non-ASCII digits are ignored, and non-string input
    (e.g. None) gives 0.
    """
    if not isinstance(text, str):
        return 0
    total = 0
    for part in text.split(";"):
        part = part.strip()
        # ASCII digits only: rejects "", "-5", "1.5", "1_000", "٣" etc.
        if part and part.isascii() and part.isdigit():
            try:
                total += int(part)
            except ValueError:  # e.g. absurdly long digit strings
                continue
    return total


def driver_age(dob, current_year=2026):
    """
    Works out the driver's age from a DD/MM/YYYY date of birth.

    Never raises. Returns None when dob is not a string, is not exactly three
    '/'-separated numeric parts, is not a real calendar date, is in the
    future, or gives an unrealistic age (> 150).
    """
    if not isinstance(dob, str):
        return None
    parts = dob.strip().split("/")
    if len(parts) != 3:
        return None
    if not all(p.isascii() and p.isdigit() for p in parts):
        return None
    try:
        day, month, year = (int(p) for p in parts)
        datetime.date(year, month, day)  # validates day/month/year
    except (ValueError, OverflowError):
        return None
    age = current_year - year
    if age < 0 or age > 150:
        return None
    return age


def main():
    print("==== Running normalize_registration ====")
    value = input("Enter a registration number (e.g. ka 01 ab 1234): ")
    print("Normalized registration:", normalize_registration(value))

    print("\n==== Running total_claim_amount ====")
    value = input("Enter past claim amounts separated by ; (e.g. 12000;4500;800): ")
    print("Total claimed:", total_claim_amount(value))

    print("\n==== Running driver_age ====")
    value = input("Enter the driver's date of birth as DD/MM/YYYY (e.g. 14/08/1999): ")
    age = driver_age(value)
    if age is None:
        print("Invalid date of birth.")
    else:
        print("Driver age in 2026:", age)


if __name__ == "__main__":
    main()
