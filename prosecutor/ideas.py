"""python3 -m prosecutor.ideas dev|held <variant,...> [n]  -> markdown rows."""
import sys
from .harness import POLICIES, play, summarize
from .monitor import ProsecutorV2
from .v3 import ProsecutorV3

V = {"v2": lambda: ProsecutorV2(),
     "count0.5": lambda: ProsecutorV3(count_w=0.5), "count1": lambda: ProsecutorV3(count_w=1.0),
     "probe": lambda: ProsecutorV3(probe=True),
     "end0.1": lambda: ProsecutorV3(end_drop=0.1), "end0.2": lambda: ProsecutorV3(end_drop=0.2),
     "all": lambda: ProsecutorV3(count_w=1.0, probe=True, end_drop=0.1)}
split, names, n = sys.argv[1], sys.argv[2].split(","), int(sys.argv[3])
seed = 1000 if split == "dev" else 2026
for v in names:
    for pol in ("honest-shaped", "sneaky", "late-big", "classic"):
        s = summarize([play(seed, g, V[v], POLICIES[pol], True, "median") for g in range(n)])
        print(f"| {v} | {pol} | {split} n={n} | {s['caught']}/{n} ({100*s['catch_rate']:.1f}%) | {s['median_round']} | "
              f"{s['false_q']:.2f} | {s['ledger']:.0f} | {s['extra_calls']:.1f} |", flush=True)
