#!/usr/bin/env python3
"""
CS 163 Fall 2026 - Concept Checker

Scans student Python files for concepts from chapters not yet covered.
Always exits 0 - never fails the workflow it runs in.
Violations and commit count are saved to concept_check_report.json.

HOW THIS GETS RUN IS NOT YET SETTLED FOR FALL 2026. Summer 2026 invoked it as
a step in a hand-written workflow that uploaded the JSON as an Actions
artifact. Classroom50 generates its own workflow, so that step no longer
exists. See TESTS.md for the two candidate approaches. Until one is wired up
and tested, the auto-zero policy below is not actually enforced.

Grading policy lives in github-grader/config.yaml, not here. As of Fall 2026
`concept_check.auto_zero_on_violation` is true, so a violation reported by this
script results in a zero for the project after instructor review.

FALL 2026 STATUS
----------------
Only the Project 1 entry in FORBIDDEN_BY_PROJECT has been verified against the
Fall 2026 schedule (P1 = Chapters 1-2). Entries for projects 2 through 5 are
carried over from Summer 2026 and MUST be re-checked before those projects are
released.

Usage:
    python3 cs163_fall2026_concept_checker.py --project N [file1.py ...]

    If no files are specified, all .py files in the current directory are
    scanned, excluding provided files and test infrastructure.
"""

import ast
import sys
import json
import argparse
import os
import fnmatch
import subprocess
from pathlib import Path
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Forbidden concept map by project number
# Each entry: AST node class name -> plain-language description
#
# Fall 2026 mapping:
#   P1 - Ch. 1-2:   Intro, Variables & Expressions          [VERIFIED]
#   P2 - Ch. 3-4:   Types, Branching                        [carried over]
#   P3 - Ch. 5-6:   Loops, Strings                          [carried over]
#   P4 - Ch. 7-8:   Functions, Files                        [carried over]
#   P5 - Ch. 9-10 (+11): Classes, Inheritance, Exceptions   [carried over]
# ---------------------------------------------------------------------------

FORBIDDEN_BY_PROJECT: dict[int, dict[str, str]] = {
    1: {
        "FunctionDef":      "function definition",
        "AsyncFunctionDef": "async function definition",
        "Lambda":           "lambda function",
        "ClassDef":         "class definition",
        "For":              "for loop",
        "While":            "while loop",
        "If":               "if/elif/else statement",
        "IfExp":            "conditional expression (a if b else c)",
        "Match":            "match/case statement",
        "Import":           "import statement",
        "ImportFrom":       "from...import statement",
        "Try":              "try/except block",
        "With":             "with statement",
        "ListComp":         "list comprehension",
        "DictComp":         "dict comprehension",
        "SetComp":          "set comprehension",
        "GeneratorExp":     "generator expression",
    },
    2: {
        "FunctionDef":      "function definition",
        "AsyncFunctionDef": "async function definition",
        "Lambda":           "lambda function",
        "ClassDef":         "class definition",
        "For":              "for loop",
        "While":            "while loop",
        "Match":            "match/case statement",
        "Import":           "import statement",
        "ImportFrom":       "from...import statement",
        "Try":              "try/except block",
        "With":             "with statement",
        "ListComp":         "list comprehension",
        "DictComp":         "dict comprehension",
        "SetComp":          "set comprehension",
        "GeneratorExp":     "generator expression",
    },
    3: {
        "FunctionDef":      "function definition",
        "AsyncFunctionDef": "async function definition",
        "Lambda":           "lambda function",
        "ClassDef":         "class definition",
        "Import":           "import statement",
        "ImportFrom":       "from...import statement",
        "Try":              "try/except block",
        "With":             "with statement",
    },
    4: {
        "ClassDef":         "class definition",
        "Import":           "import statement",
        "ImportFrom":       "from...import statement",
        "Try":              "try/except block",
    },
    5: {},
}

CHAPTER_REF: dict[str, str] = {
    "FunctionDef":      "Ch. 7",
    "AsyncFunctionDef": "Ch. 7",
    "Lambda":           "Ch. 7",
    "ClassDef":         "Ch. 9",
    "For":              "Ch. 5",
    "While":            "Ch. 5",
    "If":               "Ch. 4",
    "IfExp":            "Ch. 4",
    "Match":            "Ch. 4",
    "Import":           "Ch. 12",
    "ImportFrom":       "Ch. 12",
    "Try":              "Ch. 11",
    "With":             "Ch. 8",
    "ListComp":         "Ch. 5",
    "DictComp":         "Ch. 5",
    "SetComp":          "Ch. 5",
    "GeneratorExp":     "Ch. 5",
}

# Files provided to students - never scan these.
# check.py is the local test runner shipped in the Project 1 starter. It uses
# imports, functions, loops and conditionals by design, so scanning it would
# report violations against every student.
EXCLUDED_FILES: set[str] = {
    "cs163_fall2026_concept_checker.py",
    "concept_checker.py",
    "check.py",
    # Test infrastructure
    "conftest.py",
    "test_*.py",
    "*_test.py",
}

# One initial commit is created by "Use this template", so the floor of 4 total
# means 3 student commits. Kept in step with the autograder's commit-count test:
#     git rev-list --no-merges --count HEAD >= 4
MIN_COMMITS = 4


def should_exclude(filepath: str) -> bool:
    name = os.path.basename(filepath)
    for pattern in EXCLUDED_FILES:
        if "*" in pattern:
            if fnmatch.fnmatch(name, pattern):
                return True
        elif name == pattern:
            return True
    return False


def check_file(filepath: str, project: int) -> list[dict]:
    forbidden = FORBIDDEN_BY_PROJECT.get(project, {})
    if not forbidden:
        return []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except OSError as e:
        return [{"file": os.path.basename(filepath), "line": 0,
                 "node_type": "READ_ERROR",
                 "description": f"Could not read file: {e}", "chapter": "N/A"}]
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    violations = []
    for node in ast.walk(tree):
        node_type = type(node).__name__
        if node_type in forbidden:
            violations.append({
                "file": os.path.basename(filepath),
                "line": getattr(node, "lineno", 0),
                "node_type": node_type,
                "description": forbidden[node_type],
                "chapter": CHAPTER_REF.get(node_type, "?"),
            })
    return violations


def is_shallow() -> bool:
    """True if this is a shallow clone, where the commit count is meaningless.

    CI checkouts often default to fetch-depth 1. In that case `git rev-list
    --count HEAD` returns 1 regardless of how many commits the student made,
    which would flag every student in the class as low-commit.
    """
    try:
        r = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() == "true"
    except Exception:
        return False


def get_commit_count() -> int:
    """Student-authored commits, excluding merge commits.

    Matches the autograder's check. `git log --oneline | wc -l` was used in
    Summer 2026 and over-counted, since it included the template's initial
    commit and any merge commit from the feedback pull request.
    """
    try:
        result = subprocess.run(
            ["git", "rev-list", "--no-merges", "--count", "HEAD"],
            capture_output=True, text=True, timeout=10)
        return int(result.stdout.strip())
    except Exception:
        return -1


def collect_files(explicit: list[str]) -> list[str]:
    if explicit:
        return [f for f in explicit if not should_exclude(f) and os.path.isfile(f)]
    found = []
    for p in Path(".").rglob("*.py"):
        if should_exclude(str(p)):
            continue
        # Compare path PARTS, not a string prefix. On Windows, rglob yields
        # backslash-separated paths, so startswith("tests/") never matched.
        parts = set(p.parts)
        if ".github" in parts or "tests" in parts or "__pycache__" in parts:
            continue
        found.append(str(p))
    return sorted(found)


def main() -> None:
    parser = argparse.ArgumentParser(description="CS 163 Fall 2026 Concept Checker")
    parser.add_argument("--project", type=int, required=True, choices=[1, 2, 3, 4, 5])
    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    files = collect_files(args.files)
    all_violations: list[dict] = []
    for filepath in files:
        all_violations.extend(check_file(filepath, args.project))

    commit_count = get_commit_count()
    shallow = is_shallow()
    # Never flag on a shallow clone: the count is capped at 1 by the checkout
    # depth, not by the student, so flagging would hit the whole class.
    low_commits = (not shallow) and (commit_count >= 0) and (commit_count < MIN_COMMITS)

    report = {
        "project":         args.project,
        "checked_at":      datetime.now(timezone.utc).isoformat(),
        "files_checked":   [os.path.basename(f) for f in files],
        "commit_count":    commit_count,
        "shallow_clone":   shallow,
        "low_commit_flag": low_commits,
        "violation_count": len(all_violations),
        "violations":      all_violations,
        "flag_for_review": len(all_violations) > 0 or low_commits,
    }

    with open("concept_check_report.json", "w") as f:
        json.dump(report, f, indent=2)

    if report["flag_for_review"]:
        print("=" * 60)
        print(f"CONCEPT CHECK - Project {args.project}")
        print(f"Files:   {', '.join(report['files_checked']) or 'none found'}")
        print(f"Commits: {commit_count if commit_count >= 0 else 'unknown'}")
        print("=" * 60)
        if all_violations:
            print(f"VIOLATIONS ({len(all_violations)} found):")
            for v in all_violations:
                print(f"  {v['file']}:{v['line']}  {v['description']}  [{v['chapter']}]")
        if low_commits:
            print(f"LOW COMMIT COUNT: {commit_count} (expected >= {MIN_COMMITS})")
        print("=" * 60)
        print("Flagged for instructor review. See concept_check_report.json.")
    else:
        print(f"[concept check] Project {args.project} - "
              f"{len(files)} file(s), {commit_count} commits - no flags.")

    sys.exit(0)


if __name__ == "__main__":
    main()
