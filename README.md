# COMP 163 - Project 1: Paycheck Calculator

Write a program that figures out an employee's pay for one week.

> **If anything here disagrees with the instructions on Canvas, Canvas is
> correct.** This file exists so the exact output format sits next to your code.
> Canvas has the full assignment description, the grading breakdown, and any
> updates posted after the project was released.

## What your program does

Read four values from the user, in this exact order:

| # | Value | Example |
|---|---|---|
| 1 | Employee name | `Jordan Blake` |
| 2 | Hours worked | `40` or `37.5` |
| 3 | Hourly rate | `15.00` |
| 4 | Tax rate, as a percent | `10` |

The tax rate is entered as a percent. `10` means 10 percent, not 0.10.

**Use `float()` for all three numbers, never `int()`.**

Hours can have a fraction in them: someone who works 37 and a half hours enters
`37.5`. And the hourly rate is always written with cents, like `15.00`.

`int("15.00")` crashes. Since every test supplies a rate written that way,
using `int()` anywhere on the three numbers fails **every single test**, not
just the ones with fractional hours.

Then calculate:

```
gross pay    = hours worked * hourly rate
tax withheld = gross pay * (tax rate / 100)
net pay      = gross pay - tax withheld
```

## Required output format

Your program must print these four lines, **in this order**. The tests look for
them exactly.

```
Employee: Jordan Blake
Gross pay: $600.00
Tax withheld: $60.00
Net pay: $540.00
```

Rules that will fail the tests if you get them wrong:

- **Print them in the order shown.** One test checks the order.
- **Print the employee's name.** Every test needs the `Employee:` line, because
  that is how the checker knows your program actually read the input.
- **Print each line once.** Printing several different answers to see which one
  sticks fails the test rather than passing it.
- Spelling and capitalization must match: `Gross pay`, not `Gross Pay`
- Keep the colon and the space after it
- Keep the dollar sign
- Always show **exactly two decimal places**, even for a whole number
  (`$370.00`, never `$370.0` or `$370`)
- **No comma in large numbers.** `$1,080.00` fails. It must be `$1080.00`.
  Use `{gross:.2f}`, never `{gross:,.2f}`. The comma is what breaks it.

To get two decimals, use an f-string:

```python
print(f"Gross pay: ${gross:.2f}")
```

You may prompt however you like. Prompt text is not tested, only the four
output lines above.

## Check your work before you push

```
python check.py
```

This runs the same seven cases GitHub uses and tells you which pass. It needs
nothing installed.

> **Passing on your machine does not mean you are done.** Your grade comes from
> the run on GitHub. Push your work, open the Actions tab in your repository,
> and confirm the check is green there before the deadline. If it passes locally
> and fails on GitHub, the GitHub result is the one that counts.

## What you may use

This project covers **Chapters 1 and 2 only**: variables, `input()`, arithmetic,
type conversion (`float()`, `int()`, `str()`), and `print()`.

Do **not** use:

- `if` / `elif` / `else`
- `for` or `while` loops
- functions you define yourself (`def`)
- `import`
- classes, `try`/`except`, `with`

Your program runs straight through, top to bottom, one time.

When I grade, I run an automatic check over every submission for material from
later chapters, and anything it finds results in a zero for the project. That
check runs at grading time, not when you push, so a green check on GitHub does
not mean you are clear.

If you already know how to write this with a function and a loop, save it for
Project 2, where you will need it.

## Grading (40 points)

| Item | Points |
|---|---|
| Seven test cases, 5 points each | 35 |
| File header filled in | 3 |
| At least 3 commits | 2 |

### About the header

Fill in the top of `paycheck.py`:

```python
# Name: Your Name
# Date: 2026-09-18
```

Put your name **after** the `# Name:` label and leave the label itself in
place. The check looks for text following it, so an empty `# Name:` does not
count.

### About the commits

You get 2 points for making at least three commits. This is not busywork and it
is not about the number.

A commit is a save point you can come back to. When you break something at
11pm, the ability to return to the last version that worked is the difference
between a small problem and starting over. Commits are also the record of how
the work actually happened, which matters when you are asked to show your
process, and it is how you would hand work to someone else on a team.

Commit when you finish a piece, not all at once at the end:

```
git add paycheck.py
git commit -m "Read the four input values"
git push
```

Three is the floor, not the goal.

## Submitting

Two steps, and you need both:

1. **Push to this repository.** Every push runs the checks automatically, and
   the most recent push before the deadline is what gets graded.
2. **Paste this repository's URL into the Canvas assignment.**

The URL by itself grades nothing. It tells me which repository is yours.
Push early and push often.
