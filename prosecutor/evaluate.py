#!/usr/bin/env python3
"""Run baseline vs Prosecutor on frozen held-out games, normal and sneaky rogues.

  python3 -m prosecutor.evaluate              # table + data/results.json for the dashboard
  python3 -m prosecutor.evaluate --tune       # threshold sweep on DEV seeds only

Dev seed (tuning only): 1000. Held-out seed (reporting): 2026, games 0..N-1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os

from .harness import POLICIES, play, summarize
from .monitor import Baseline, Prosecutor

DEV_SEED, HELDOUT_SEED = 1000, 2026


def configs(tau):
    return {
        "Baseline": (lambda: Baseline(), False, False),
        "Prosecutor (no retrial)": (lambda: Prosecutor(tau=tau, use_retrial=False), False, False),
        "Prosecutor": (lambda: Prosecutor(tau=tau), True, False),
        "Prosecutor + repair": (lambda: Prosecutor(tau=tau), True, True),
    }


def run(seed, n, tau, policies):
    res = {}
    for pol in policies:
        for name, (fac, retrial, repair) in configs(tau).items():
            games = [play(seed, g, fac, POLICIES[pol], retrial, repair) for g in range(n)]
            res[(pol, name)] = games
    return res


def fmt(s):
    lo, hi = s["catch_ci"]
    return (f"{s['caught']}/{s['n']} ({100*s['catch_rate']:.0f}%, CI {100*lo:.0f}-{100*hi:.0f})",
            f"{s['median_round']}", f"{s['mean_round_miss13']:.1f}",
            f"{s['false_q']:.2f} ({s['false_q_ci'][0]:.2f}-{s['false_q_ci'][1]:.2f})",
            f"{s['ledger']:.0f} ({s['ledger_ci'][0]:.0f}-{s['ledger_ci'][1]:.0f})",
            f"{s['extra_calls']:.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=500)
    ap.add_argument("--tau", type=float, default=0.55)
    ap.add_argument("--tune", action="store_true")
    ap.add_argument("--out", default="data/results.json")
    args = ap.parse_args()

    if args.tune:
        print("DEV seed sweep (classic + sneaky). tau | catch | fq/game | ledger")
        for tau in (0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 0.99):
            for pol in ("classic", "sneaky"):
                g = [play(DEV_SEED, i, lambda: Prosecutor(tau=tau), POLICIES[pol], True) for i in range(args.games)]
                s = summarize(g)
                print(f"{tau:.2f} {pol:8s} {s['catch_rate']:.2f} {s['false_q']:.2f} {s['ledger']:.0f}")
        return

    ids = hashlib.sha256(f"{HELDOUT_SEED}:{args.games}".encode()).hexdigest()[:12]
    print(f"Held-out: seed {HELDOUT_SEED}, games 0..{args.games-1} (hash {ids}); tau={args.tau} chosen on dev seed {DEV_SEED}\n")
    policies = list(POLICIES)
    res = run(HELDOUT_SEED, args.games, args.tau, policies)
    hdr = "| Rogue | Monitor | Rogue caught | Median round | Mean round (miss=13) | False quarantines/game | Mean ledger error | Extra calls/game |"
    print(hdr)
    print("|" + "---|" * 8)
    summary = {}
    for (pol, name), games in res.items():
        s = summarize(games)
        summary[f"{pol}|{name}"] = s
        print(f"| {pol} | {name} | " + " | ".join(fmt(s)) + " |")

    # Dashboard data: summaries + a sample of full games per (policy, monitor), plus τ sweep
    sweep = []
    for tau in (0.5, 0.7, 0.8, 0.9, 0.95, 0.98, 0.995):
        for pol in ("classic", "sneaky"):
            g = [play(HELDOUT_SEED, i, lambda: Prosecutor(tau=tau), POLICIES[pol], True) for i in range(200)]
            s = summarize(g)
            sweep.append({"tau": tau, "policy": pol, "catch": s["catch_rate"], "fq": s["false_q"]})
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    sample = {f"{pol}|{name}": games[:60] for (pol, name), games in res.items()}
    with open(args.out, "w") as f:
        json.dump({"heldout_seed": HELDOUT_SEED, "games": args.games, "hash": ids, "tau": args.tau,
                   "summary": summary, "sweep": sweep, "sample": sample}, f, default=str)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
