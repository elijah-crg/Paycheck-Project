#!/usr/bin/env python3
"""
COMP 163 Project 1 - Local Test Runner

Run this to check your work before you push:

    python check.py        (or python3 check.py)

It runs paycheck.py against the same seven cases GitHub uses, with the same
rules, and tells you which ones pass. Standard library only, nothing to install.

IMPORTANT: passing here does not mean you are done. Your work is graded by
the run on GitHub. Push your code and confirm the check is green there.
"""
import os
import re
import subprocess
import sys

PROGRAM = "paycheck.py"

# (case label, stdin lines, required lines, enforce_order)
# Every case requires the Employee line: that is how the checker knows your
# program read the input instead of printing a memorized answer.
CASES = [
    ("40 hours at $15.00, 10% tax (checks all four lines, in order)",
     ["Jordan Blake", "40", "15.00", "10"],
     ["Employee: Jordan Blake", "Gross pay: $600.00",
      "Tax withheld: $60.00", "Net pay: $540.00"], True),
    ("37.5 hours at $20.00, 12% tax",
     ["Alex Rivera", "37.5", "20.00", "12"],
     ["Employee: Alex Rivera", "Net pay: $660.00"], False),
    ("20 hours at $18.50, no tax",
     ["Sam Chen", "20", "18.50", "0"],
     ["Employee: Sam Chen", "Net pay: $370.00"], False),
    ("45 hours at $32.00, 25% tax",
     ["Taylor Reed", "45", "32.00", "25"],
     ["Employee: Taylor Reed", "Net pay: $1080.00"], False),
    ("10.25 hours at $16.00, 8% tax",
     ["Morgan Lee", "10.25", "16.00", "8"],
     ["Employee: Morgan Lee", "Net pay: $150.88"], False),
    ("38 hours at $21.50, 15% tax (checks gross pay)",
     ["Casey Kim", "38", "21.50", "15"],
     ["Employee: Casey Kim", "Gross pay: $817.00"], False),
    ("52.5 hours at $27.40, 18% tax (checks tax withheld)",
     ["Riley Novak", "52.5", "27.40", "18"],
     ["Employee: Riley Novak", "Tax withheld: $258.93"], False),
]


def run_case(stdin_lines):
    """Return (stdout, error_message). error_message is None on success."""
    try:
        result = subprocess.run(
            [sys.executable, PROGRAM],
            input="\n".join(stdin_lines) + "\n",
            capture_output=True, text=True, timeout=10,
        )
    except subprocess.TimeoutExpired:
        return None, ("Your program never finished. If it has a loop in it, "
                      "remove it - this project runs top to bottom once.")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "EOFError" in stderr:
            return None, ("Your program asked for more input than it was given. "
                          "You should have exactly four input() calls.")
        if "ValueError" in stderr and "int()" in stderr:
            return None, ("int() cannot read a number written with a decimal "
                          "point, like 37.5 or 15.00. Use float() for all three "
                          "numbers.")
        tail = stderr.splitlines()[-3:] or ["(no error message)"]
        return None, "Your program crashed:\n      " + "\n      ".join(tail)

    return result.stdout, None


def problems_with(stdout, required, enforce_order):
    """Same rules the GitHub check uses. Returns a list of complaints."""
    issues = []
    for want in required:
        # (?!\d) matters: "Net pay: $540.00" is a substring of "$540.000",
        # so a plain `in` test would accept three decimals that GitHub rejects.
        if not re.search(re.escape(want) + r"(?!\d)", stdout):
            if want in stdout:
                issues.append(f"too many decimal places in: {want}")
            else:
                issues.append(f"missing: {want}")
    if issues:
        return issues

    # Each answer line must appear exactly once. Printing several different
    # answers to see which sticks fails on GitHub.
    for want in required:
        label = want.split(":")[0]
        if stdout.count(label + ":") > 1:
            issues.append(f"printed more than one '{label}:' line")

    if enforce_order:
        positions = [stdout.index(w) for w in required]
        if positions != sorted(positions):
            issues.append("the four lines are not in the required order "
                          "(Employee, Gross pay, Tax withheld, Net pay)")
    return issues


def main():
    print("=" * 66)
    print("COMP 163 Project 1 - checking paycheck.py")
    print("=" * 66)

    if not os.path.exists(PROGRAM):
        print(f"\nCould not find {PROGRAM} in this folder.")
        print("Run this from inside your project folder, the same place")
        print(f"{PROGRAM} lives. Do not rename {PROGRAM}: the grader looks")
        print("for that exact filename.\n")
        return

    passed = 0
    for i, (label, stdin_lines, required, ordered) in enumerate(CASES, 1):
        stdout, error = run_case(stdin_lines)

        if error:
            print(f"\n[{i}/7] FAIL  {label}")
            print(f"      {error}")
            print(f"      Input was: {', '.join(stdin_lines)}\n")
            continue

        issues = problems_with(stdout, required, ordered)
        if not issues:
            print(f"[{i}/7] PASS  {label}")
            passed += 1
        else:
            print(f"\n[{i}/7] FAIL  {label}")
            print(f"      Input:    {', '.join(stdin_lines)}")
            for m in issues:
                print(f"      {m}")
            print("      Your output was:")
            for line in (stdout.strip().splitlines() or ["(nothing)"]):
                print(f"        {line}")
            print()

    print("=" * 66)
    print(f"{passed} of {len(CASES)} cases passed")

    header_ok = False
    try:
        for line in open(PROGRAM, encoding="utf-8"):
            if line.startswith("# Name:") and line[len("# Name:"):].strip():
                header_ok = True
                break
    except OSError:
        pass
    print(f"file header filled in: {'yes' if header_ok else 'NO - worth 3 points'}")

    if passed == len(CASES) and header_ok:
        print("\nThat is 38 of the 40 points. The last 2 come from making at")
        print("least three commits of your own.")
        print("\nNow push and confirm the run is green on GitHub.")
    else:
        print("\nCheck the format in README.md. Spelling, capitalization, the")
        print("$, exactly two decimal places, no comma in large numbers, and")
        print("the order of the four lines all have to match.")
    print("=" * 66)


if __name__ == "__main__":
    main()
