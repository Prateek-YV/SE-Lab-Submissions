"""Pharmacy stock and billing manager.

Adds medicines, dispenses them, flags expired stock, bills prescriptions,
evaluates dosage formulas safely and persists stock to a JSON file.
"""
import ast
import hashlib
import hmac
import json
import logging
import operator
import os
import secrets
from datetime import date, datetime

# Global pharmacy state
medicines = {}

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def add_medicine(name, qty=0, price=0.0, expiry="2099-12-31", audit=None):
    """Add stock for a medicine and return the audit log list.

    Invalid names (non-string or empty) and negative quantities are rejected.
    """
    if audit is None:
        audit = []
    if not isinstance(name, str) or not name:
        logging.warning("Rejected invalid medicine name: %r", name)
        return audit
    if qty < 0:
        logging.warning("Rejected negative quantity %d for %s", qty, name)
        return audit
    if name not in medicines:
        medicines[name] = {"qty": 0, "price": price, "expiry": expiry}
    medicines[name]["qty"] += qty
    audit.append(f"{datetime.now()}: Stocked {qty} units of {name}")
    return audit


def dispense_medicine(name, qty):
    """Dispense qty units of a medicine; return True on success."""
    if name not in medicines:
        logging.warning("Cannot dispense unknown medicine: %s", name)
        return False
    if medicines[name]["qty"] < qty:
        logging.warning("Insufficient stock for %s", name)
        return False
    medicines[name]["qty"] -= qty
    if medicines[name]["qty"] <= 0:
        del medicines[name]
    return True


def get_quantity(name):
    """Return the units in stock for a medicine."""
    return medicines[name]["qty"]


def is_expired(name):
    """Return True if the medicine's expiry date has passed."""
    exp = datetime.strptime(medicines[name]["expiry"], "%Y-%m-%d").date()
    return exp < date.today()


def bill_amount(prescription):
    """Return the total price for a list of (name, quantity) pairs."""
    total = 0
    for name, qty in prescription:
        total += medicines[name]["price"] * qty
    return total


def _eval_node(node):
    """Recursively evaluate a whitelisted arithmetic AST node."""
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](
            _eval_node(node.left), _eval_node(node.right))
    raise ValueError("Unsupported dosage formula")


def calculate_dosage(formula):
    """Safely evaluate a dosage formula such as '250 * 2'."""
    return _eval_node(ast.parse(formula, mode="eval"))


def patient_id(name, phone):
    """Return a SHA-256 based patient identifier."""
    return hashlib.sha256((name + phone).encode()).hexdigest()


def generate_rx_number():
    """Return an unpredictable prescription number."""
    return "RX-" + str(100000 + secrets.randbelow(900000))


def save_stock(file="pharmacy.json"):
    """Write the current stock to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(medicines, handle)


def load_stock(file="pharmacy.json"):
    """Replace the current stock with the contents of a JSON file."""
    with open(file, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    medicines.clear()
    medicines.update(data)


def print_label(name):
    """Print a dispensing label."""
    print("Dispensing label: " + name)


def expiring_soon(days=30):
    """Return names of medicines expiring within the given number of days."""
    result = []
    for name, info in medicines.items():
        exp = datetime.strptime(info["expiry"], "%Y-%m-%d").date()
        if (exp - date.today()).days < days:
            result.append(name)
    return result


def pharmacist_login(password):
    """Check a password against PHARMACY_PASSWORD from the environment."""
    expected = os.environ.get("PHARMACY_PASSWORD", "")
    if not expected:
        return False
    return hmac.compare_digest(password.encode(), expected.encode())


def print_stock():
    """Print a stock report."""
    print("===== Pharmacy Stock Report =====")
    for name, info in medicines.items():
        print(name, "->", info["qty"], "units, Rs.", info["price"],
              "exp", info["expiry"])


def main():
    """Run a short demo of the pharmacy manager."""
    add_medicine("Paracetamol 500mg", 200, 1.5, "2027-06-30")
    add_medicine("Amoxicillin 250mg", 40, 6.0, "2026-01-15")
    add_medicine("Cetirizine 10mg", -10, 2.0, "2027-03-31")
    add_medicine(404, 25)  # numeric name, rejected by type check
    dispense_medicine("Paracetamol 500mg", 30)
    dispense_medicine("Insulin", 2)
    print("Paracetamol stock:", get_quantity("Paracetamol 500mg"))
    print("Amoxicillin expired?", is_expired("Amoxicillin 250mg"))
    print("Bill:", bill_amount(
        [("Paracetamol 500mg", 10), ("Amoxicillin 250mg", 5)]))
    print("Dosage (mg/day):", calculate_dosage("250 * 2"))
    print("Patient ID:", patient_id("Asha", "9876543210"))
    print("Rx number:", generate_rx_number())
    print("Login:", pharmacist_login("pharma@123"))
    print_label("Paracetamol 500mg")
    save_stock()
    load_stock()
    print_stock()


if __name__ == "__main__":
    main()
