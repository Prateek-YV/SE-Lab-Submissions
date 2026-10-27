# Lab 5: Reflection

The handout PDF did not list the reflection questions in its text, so these answers cover the four standard questions for this lab. If your copy words them differently, the answers below can be matched to them.

## 1. Which issues were the easiest and which were the hardest to fix?

The easiest were the mechanical ones: Flake8 blank-line and line-length warnings, unused imports, snake_case renames and docstrings. Many of these can be fixed automatically (autopep8 handled the blank lines) and carry no risk of changing behaviour.

The hardest were the security fixes that needed a redesign rather than a one-line change. Replacing `eval` meant writing a small AST evaluator that allows only numbers and arithmetic operators. Replacing `pickle` meant changing the file format to JSON. Removing the hardcoded password meant deciding where the secret should live (an environment variable) and making login fail safely when it is missing.

## 2. Did the tools report any false positives, or miss anything?

Mostly the findings were real, but severity does not always match risk. Bandit marks `random.randint` (B311) and the `pickle` import (B403) as Low, yet using them for prescription numbers and for stock files is a real weakness in this program. The MD5 finding (B324) is High even though a hash used as an ID is less dangerous than one used for passwords, so context matters. The hardcoded password finding was only Low severity and Medium confidence, but it is the kind of leak that matters most in a real repository.

The tools missed the logic bugs entirely. Running the program showed a stock of `-10` units, a medicine called `404`, and a silent failure when dispensing "Insulin". Only the mutable default `audit=[]` and the inconsistent return were flagged (by Pylint), and the other bugs were found by reading the output.

## 3. How could static analysis fit into your normal development workflow?

Run Flake8 and Pylint locally as an editor plugin or pre-commit hook so style and quality problems are fixed while the code is fresh. Run Bandit, Flake8 and Pylint again in CI on every pull request, with a minimum Pylint score and a rule that Bandit High and Medium findings fail the build. Commit the reports or keep them as CI artifacts so progress can be compared over time. Findings that are deliberately accepted should be suppressed with a documented `# nosec` or `# pylint: disable` comment and a reason, not ignored.

## 4. What tangible improvements did you see in the code after the fixes?

- Pylint went from 4.83/10 to 10.00/10, Bandit from 8 findings (2 High) to 0, and Flake8 from 22 warnings to 0.
- The program can no longer run arbitrary code through the dosage formula, run shell commands through a medicine name, or execute code from a tampered stock file.
- The password is no longer in source control.
- Bad input is now rejected (negative quantities, non-string names, over-dispensing) and logged instead of corrupting stock or failing silently.
- Code is easier to read and maintain: consistent names, docstrings, no shared global reassignment, no code running on import, and files closed safely.
- The demo output is still correct (stock 170, bill 45.0, dosage 500).

Static analysis does not replace running and reading the program, but it made the review faster and caught the dangerous patterns reliably.
