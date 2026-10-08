"""Signed percentage formatting, in one place.

THE RULE

Round first, then decide the sign. If the rounded value is 0.0, print "0.0%" with no sign.

Order matters, and getting it backwards is what puts "-0.0%" on a page. Formatting first and
rounding second means the value is genuinely negative, so the sign is correct, and then the
decimal rounds away to nothing and leaves a sign attached to a zero. The card reads "-0.0%",
which tells a reader the number moved when it did not.

    round(-0.04, 1)  ->  -0.0  ->  "0.0%"    not "-0.0%"
    round( 0.04, 1)  ->   0.0  ->  "0.0%"    not "+0.0%"
    round(-0.06, 1)  ->  -0.1  ->  "-0.1%"
    round( 3.015, 1) ->   3.0  ->  "+3.0%"

normalize.py has always done this correctly for one figure - the provincial comparison uses
`f"{diff:+.1f}" if diff else "0.0"` - but the percentage figures were written separately and
never picked the same rule up.

ONE FUNCTION, SO THE NEXT CARD CANNOT MISS IT

Five format strings across four modules were doing this by hand. They now call pct().
"""
import math


def pct(v, decimals=1):
    """A signed percentage: rounded before the sign is chosen, and unsigned when it is zero.

    Returns "n/a" for anything that is not a number, matching how the rest of the build treats
    a missing reading. A missing figure is never rendered as 0.0%.
    """
    if v is None:
        return "n/a"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "n/a"
    if math.isnan(v) or math.isinf(v):
        return "n/a"

    r = round(v, decimals)
    # r == 0 is true for -0.0 as well, which is the whole point: a negative value that rounds
    # to nothing is a zero, and a zero carries no sign.
    if r == 0:
        return f"{0.0:.{decimals}f}%"
    return f"{r:+.{decimals}f}%"


def signed(v, decimals=1):
    """Same rule without the percent sign, for figures measured in cents per litre."""
    if v is None:
        return "n/a"
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "n/a"
    r = round(v, decimals)
    if r == 0:
        return f"{0.0:.{decimals}f}"
    return f"{r:+.{decimals}f}"
