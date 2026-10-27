# Lab 5: Issue Documentation

Program: `pharmacy_manager.py` (from `SETAPESU26/L5_55_pharmacy-manager`)

| Tool | Before | After |
|------|--------|-------|
| Pylint | 4.83/10 | 10.00/10 |
| Bandit | 8 issues (2 High, 2 Medium, 4 Low) | 0 issues |
| Flake8 | 22 warnings | 0 warnings |

Line numbers refer to the **original** file.

## Security issues (Bandit), fixed in commit 1

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `os.system` with string concatenation (B605) | Security, High | 68 | Medicine name is concatenated into a shell command, so a name like `x; rm -rf ~` runs arbitrary commands. | Removed the shell call; the label is printed with `print()`. |
| Weak MD5 hash for patient ID (B324) | Security, High | 51 | MD5 is broken and unsuitable for identifying patients from personal data. | Switched to `hashlib.sha256`. |
| `eval()` on doctor's note (B307, Pylint W0123) | Security, Medium | 48 | Any string reaching `calculateDosage` is executed as Python code. | Replaced with an `ast`-based evaluator that allows only numbers and `+ - * /`. Anything else raises `ValueError` (verified `__import__("os")` is blocked). |
| `pickle.load` (B301) and `import pickle` (B403) | Security, Medium/Low | 3, 64 | Unpickling a tampered `pharmacy.dat` can execute code. | Stock is now saved and loaded as JSON (`pharmacy.json`, added to `.gitignore`). |
| Hardcoded password (B105) | Security, Low | 11 | `DB_PASSWORD = "pharma@123"` is in source and version control. | Password is read from the `PHARMACY_PASSWORD` environment variable and compared with `hmac.compare_digest`. Login fails closed when it is unset. |
| `try/except/pass` with bare except (B110, E722, W0702) | Bug / Security, Low | 24-28 | Swallowed every error, so dispensing an unknown medicine such as "Insulin" or an over-dispense failed silently. | Explicit checks for unknown medicine and insufficient stock; log a warning and return `False`/`True`. |
| `random.randint` for Rx numbers (B311) | Security, Low | 54 | Predictable pseudo-random numbers for prescription IDs. | Switched to `secrets.randbelow`. |

## Logic bugs (found by running the program, not flagged by any tool), fixed in commit 1

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Mutable default argument `audit=[]` (Pylint W0102) | Bug | 13 | The audit list is shared across all calls, so logs from unrelated calls pile up. | Default to `None` and create a new list inside the function. |
| Negative quantity accepted | Bug | 18, 92 | `addMedicine("Cetirizine 10mg", -10)` produced `-10 units` in the stock report. | Reject `qty < 0` with a logged warning. |
| Numeric medicine name accepted | Bug | 93 | `addMedicine(404, 25)` created a medicine named `404`. | Reject non-string or empty names. |
| Inconsistent return (R1710) | Bug | 13-20 | Early `return` gave `None`, normal path returned the list. | Always return the audit list. |
| Over-dispensing allowed | Bug | 24-26 | Dispensing more than in stock drove quantity negative, or deleted the entry. | Refuse when stock is insufficient. |

## Style issues (Flake8), fixed in commit 2

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| E302 expected 2 blank lines (15 occurrences) | Style | 13, 22, 30, ... 89 | One blank line between top-level functions. | Two blank lines before each function. |
| E305 expected 2 blank lines after function | Style | 108 | `main()` call directly after a function. | Fixed, and later wrapped in `if __name__ == "__main__":`. |
| E501 line too long (3 occurrences) | Style | 19, 87, 98 | Lines of 81, 111 and 85 characters. | Wrapped to under 80 characters. |
| F401 unused imports `sys`, `logging` | Style | 2, 6 | Dead imports. | Removed `sys`; `logging` is now used for warnings. |

## Quality issues (Pylint), fixed in commit 3

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| C0103 invalid-name (14 functions) | Convention | 13-84 | camelCase names such as `addMedicine`. | Renamed to snake_case (`add_medicine`, `dispense_medicine`, ...). |
| C0114 / C0116 missing docstrings | Convention | 1, every function | No module or function documentation. | Added a module docstring and a docstring for every function. |
| R1732 consider-using-with | Refactor | 57, 62 | Files opened and closed manually; a failure in between leaks the handle. | `with open(...)` blocks. |
| W0603 global-statement | Warning | 63 | `global medicines` reassigns module state. | `medicines.clear()` and `medicines.update(data)`. |
| R1703 / R1705 simplifiable if, no-else-return | Refactor | 35, 79 | `if cond: return True else: return False`. | Return the boolean expression directly. |
| C0209 consider-using-f-string | Convention | 19 | `%` formatting. | f-string. |
| C0301 line too long | Convention | 87 | 111-character print line. | Wrapped. |
| Iterating keys then indexing | Style | 72, 86 | `for m in medicines: medicines[m][...]`. | Iterate with `.items()`. |
| Module code runs on import | Bug | 108 | `main()` was called at import time. | Added `if __name__ == "__main__":` guard. |

## Commits

1. `fix(bandit)`: all Bandit findings plus the logic bugs above.
2. `style(flake8)`: all Flake8 findings.
3. `refactor(pylint)`: Pylint score 4.83 to 10.00.
