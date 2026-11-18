#!/usr/bin/env python3
"""Print a baseline-versus-ours markdown table for Track 2.

Baseline cells are pre-filled from sim.py --mock --games 200 --seed 0.
Pass Prosecutor and sneakier-rogue results as flags, or leave them blank.

Example:
  python3 scaffold/scripts/table.py
  python3 scaffold/scripts/table.py --ours-caught 190 --ours-n 200 \\
      --ours-median 5 --ours-false-q 0.20 --ours-ledger 80
"""

from __future__ import annotations

import argparse
import sys


BASELINE = {
    "label": "Baseline (mock, n=200, seed 0)",
    "caught": "88% (177/200)",
    "median": "6",
    "false_q": "1.38",
    "ledger": "285",
}


def fmt_caught(caught: int | None, n: int | None) -> str:
    if caught is None or n is None or n == 0:
        return ""
    pct = 100 * caught / n
    return f"{pct:.0f}% ({caught}/{n})"


def fmt_num(value: float | None, digits: int) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}" if digits else f"{value:.0f}"


def col_label(prefix: str, n: int | None, extra: str) -> str:
    if n:
        return f"{prefix} (n={n}{', ' + extra if extra else ''})"
    return prefix


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ours-caught", type=int, default=None, help="rogues caught by Prosecutor")
    p.add_argument("--ours-n", type=int, default=None, help="Prosecutor mock games")
    p.add_argument("--ours-median", type=float, default=None)
    p.add_argument("--ours-false-q", type=float, default=None, help="false quarantines per game")
    p.add_argument("--ours-ledger", type=float, default=None, help="mean ledger error")
    p.add_argument("--ours-note", default="mock", help="short label note, default: mock")
    p.add_argument("--base-sneaky-caught", type=int, default=None)
    p.add_argument("--base-sneaky-n", type=int, default=None)
    p.add_argument("--base-sneaky-median", type=float, default=None)
    p.add_argument("--base-sneaky-false-q", type=float, default=None)
    p.add_argument("--base-sneaky-ledger", type=float, default=None)
    p.add_argument("--ours-sneaky-caught", type=int, default=None)
    p.add_argument("--ours-sneaky-n", type=int, default=None)
    p.add_argument("--ours-sneaky-median", type=float, default=None)
    p.add_argument("--ours-sneaky-false-q", type=float, default=None)
    p.add_argument("--ours-sneaky-ledger", type=float, default=None)
    args = p.parse_args(argv)

    ours = {
        "label": col_label("Prosecutor", args.ours_n, args.ours_note),
        "caught": fmt_caught(args.ours_caught, args.ours_n),
        "median": "" if args.ours_median is None else (str(int(args.ours_median)) if args.ours_median == int(args.ours_median) else str(args.ours_median)),
        "false_q": fmt_num(args.ours_false_q, 2),
        "ledger": fmt_num(args.ours_ledger, 0),
    }
    base_s = {
        "label": col_label("Baseline vs sneaky", args.base_sneaky_n, ""),
        "caught": fmt_caught(args.base_sneaky_caught, args.base_sneaky_n),
        "median": "" if args.base_sneaky_median is None else str(args.base_sneaky_median),
        "false_q": fmt_num(args.base_sneaky_false_q, 2),
        "ledger": fmt_num(args.base_sneaky_ledger, 0),
    }
    ours_s = {
        "label": col_label("Prosecutor vs sneaky", args.ours_sneaky_n, ""),
        "caught": fmt_caught(args.ours_sneaky_caught, args.ours_sneaky_n),
        "median": "" if args.ours_sneaky_median is None else str(args.ours_sneaky_median),
        "false_q": fmt_num(args.ours_sneaky_false_q, 2),
        "ledger": fmt_num(args.ours_sneaky_ledger, 0),
    }

    cols = [BASELINE, ours, base_s, ours_s]
    headers = ["Metric"] + [c["label"] for c in cols]
    rows = [
        ["Rogue caught"] + [c["caught"] for c in cols],
        ["Median round caught"] + [c["median"] for c in cols],
        ["False quarantines / game"] + [c["false_q"] for c in cols],
        ["Mean ledger error"] + [c["ledger"] for c in cols],
    ]

    def line(cells: list[str]) -> str:
        return "| " + " | ".join(cells) + " |"

    print(line(headers))
    print("|" + "|".join(["---"] * len(headers)) + "|")
    for row in rows:
        print(line(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
