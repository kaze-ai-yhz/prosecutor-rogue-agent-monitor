"""Parallel runner for v2 tuning / held-out tables.
  python3 scripts/run_v2.py tune            # DEV seed 1000, classic/sneaky/honest-shaped
  python3 scripts/run_v2.py report [n]      # seeds 2026, 7777: Baseline / v1+repair / v2, all policies
  python3 scripts/run_v2.py ablate [n]      # seed 2026: v2 minus each component
"""
import itertools, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool
from prosecutor.harness import POLICIES, play, summarize
from prosecutor.monitor import Baseline, Prosecutor, ProsecutorV2

V2 = dict(tau=0.5, mag_w=0.7, cp_weight=0.5)  # overwritten from tuned.json if present
TF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tuned.json")
if os.path.exists(TF):
    V2.update(json.load(open(TF)))


def make(spec):
    kind, kw = spec
    if kind == "base":
        return Baseline()
    if kind == "v1":
        return Prosecutor(tau=0.55)
    return ProsecutorV2(**kw)


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
    if mode == "tune":
        jobs = []
        for tau, mw, cw in itertools.product((0.4, 0.5, 0.6, 0.7), (0.5, 0.7, 1.0), (0.3, 0.5, 0.7)):
            kw = dict(tau=tau, mag_w=mw, cp_weight=cw)
            for pol in ("classic", "sneaky", "honest-shaped"):
                jobs.append((1000, n, pol, json.dumps(kw), ("v2", kw), True, "median"))
        go(jobs)
    elif mode == "report":
        jobs = []
        for seed in (2026, 7777):
            for pol in POLICIES:
                jobs += [(seed, n, pol, "Baseline", ("base", {}), False, False),
                         (seed, n, pol, "Prosecutor v1 + repair", ("v1", {}), True, True),
                         (seed, n, pol, "Prosecutor v2", ("v2", V2), True, "median")]
        go(jobs)
    elif mode == "ablate":
        jobs = []
        abl = {"v2 full": ({}, "median"), "v2 - magnitude": ({"magnitude": False}, "median"),
               "v2 - antiframe": ({"antiframe": False}, "median"),
               "v2 - recency": ({"recency": False}, "median"),
               "v2 - median-commit (majority repair)": ({}, True)}
        for pol in ("classic", "sneaky", "late-big", "framer"):
            for label, (kw, rep) in abl.items():
                jobs.append((2026, n, pol, label, ("v2", {**V2, **kw}), True, rep))
        go(jobs)
