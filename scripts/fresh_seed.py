"""Independent check: Baseline vs Prosecutor v2 on seeds the team never used (not 1000, not 2026).

usage: python3 fresh_seed.py <repo> <seed> <games>
Uses the team's own harness (play, summarize) so the game rules are identical; only the seed is new.
"""
import sys
sys.path.insert(0, sys.argv[1])
from prosecutor.harness import POLICIES, play, summarize
from prosecutor.monitor import Baseline, ProsecutorV2

seed, n = int(sys.argv[2]), int(sys.argv[3])
print(f"fresh seed {seed}, n={n} games per row")
for pol in POLICIES:
    for name, fac, retrial, repair in (("Baseline", lambda: Baseline(), False, False),
                                       ("Prosecutor v2", lambda: ProsecutorV2(), True, "median")):
        s = summarize([play(seed, g, fac, POLICIES[pol], retrial, repair) for g in range(n)])
        lo, hi = s["catch_ci"]
        print(f"{pol:14s} | {name:14s} | {s['caught']}/{s['n']} ({100*s['catch_rate']:.1f}%, CI {100*lo:.0f}-{100*hi:.0f}) "
              f"| R{s['median_round']} | fq {s['false_q']:.2f} | ledger {s['ledger']:.1f} | extra {s['extra_calls']:.1f}", flush=True)
