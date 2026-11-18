"""v3 runner (ProsecutorV3 = v2 + late_prior + late_decision).
  python3 scripts/run_v3.py check [n]    # V3 with flags off == v2 (identity, seed 2026)
  python3 scripts/run_v3.py tune [n]     # DEV seed 1000, classic/sneaky/honest-shaped only (joint)
  python3 scripts/run_v3.py report [n]   # seeds 2026, 7777: Baseline / v2 / v3, all five policies
  python3 scripts/run_v3.py ablate [n]   # seed 2026: v3 minus each component, all five policies
"""
import itertools, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool
from prosecutor.harness import POLICIES, play, summarize
from prosecutor.monitor import Baseline, ProsecutorV2, ProsecutorV3

HERE = os.path.dirname(os.path.abspath(__file__))
V2 = json.load(open(os.path.join(HERE, "tuned.json")))
V3F = os.path.join(HERE, "tuned_v3.json")
V3 = json.load(open(V3F)) if os.path.exists(V3F) else dict(V2)
DEV = ("classic", "sneaky", "honest-shaped")


def make(spec):
    kind, kw = spec
    if kind == "base":
        return Baseline()
    if kind == "v2":
        return ProsecutorV2(**kw)
    return ProsecutorV3(**kw)


def job(a):
    seed, n, pol, label, spec, retrial, repair = a
    gs = [play(seed, g, lambda: make(spec), POLICIES[pol], retrial, repair) for g in range(n)]
    s = summarize(gs)
    return dict(seed=seed, policy=pol, monitor=label, caught_pct=round(100 * s["catch_rate"], 1),
                median_round=s["median_round"], false_q=round(s["false_q"], 3),
                ledger=round(s["ledger"], 1), extra_calls=round(s["extra_calls"], 2))


def go(jobs):
    with Pool() as p:
        out = p.map(job, jobs)
    for r in out:
        print(json.dumps(r), flush=True)
    return out


if __name__ == "__main__":
    mode = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    if mode == "check":
        go([(2026, n, p, l, s, True, "median") for p in POLICIES
             for l, s in (("v2", ("v2", V2)), ("v3 flags off", ("v3", V2)))])
    elif mode == "tune":
        grid = [dict(V2, tau=t, cp_gamma=g, late_tau=lt, late_from=lf)
                for t in (0.6, 0.7, 0.8) for g in (0.0, 1.0, 2.0, 3.0)
                for lt, lf in ((None, 11), (0.6, 11), (0.5, 11), (0.6, 10), (0.5, 12))
                if lt is None or lt < t]
        go([(1000, n, pol, json.dumps(kw), ("v3", kw), True, "median") for kw in grid for pol in DEV])
    elif mode == "report":
        jobs = []
        for seed in (2026, 7777):
            for pol in POLICIES:
                jobs += [(seed, n, pol, "Baseline", ("base", {}), False, False),
                         (seed, n, pol, "Prosecutor v2", ("v2", V2), True, "median"),
                         (seed, n, pol, "Prosecutor v3", ("v3", V3), True, "median")]
        go(jobs)
    elif mode == "ablate":
        abl = {"v3 full": {}, "v3 - late_prior": {"late_prior": False},
               "v3 - late_decision": {"late_decision": False},
               "v3 - both (=v2 + v3 tau)": {"late_prior": False, "late_decision": False}}
        go([(2026, n, pol, label, ("v3", {**V3, **kw}), True, "median")
            for pol in POLICIES for label, kw in abl.items()])
