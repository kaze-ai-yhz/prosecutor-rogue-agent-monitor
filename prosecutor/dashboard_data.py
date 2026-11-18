"""Build the compact JSON the dashboard reads (truth is used here only for scoring, never by the monitor)."""
import json, sys
from .harness import POLICIES, play, summarize
from .monitor import Baseline, Prosecutor, ProsecutorV2
from .evaluate import HELDOUT_SEED

TAU = 0.7  # ProsecutorV2 default, tuned on dev seed 1000
POLICY_ORDER = ("classic", "sneaky", "honest-shaped", "late-big", "framer")
N_SHOW = 40


def impacts(rnd):
    """Signed push of each answering agent on this round's ledger."""
    # Each answer is half of the averaged total, so an agent pushes the ledger by
    # (answer - truth) / 2. This is what the agent tried to do, before any repair.
    return {n: (a["answer"] - rnd["truth"]) / 2 for n, a in rnd["answers"].items()}


def autopsy(games):
    """Where the damage lands (per game averages) and why rogues were missed."""
    n = len(games)
    bands = {"R1-4": 0.0, "R5-8": 0.0, "R9-12": 0.0, "honest": 0.0}
    miss = {"never lied": 0, "lied once": 0, "lied 2+": 0}
    fq_before = fq_after = 0
    for g in games:
        out = False
        for x in g["transcript"]:
            e = abs(x["team"] - x["truth"])
            if g["rogue"] in x["answers"] and x["answers"][g["rogue"]]["answer"] != x["truth"]:
                bands["R1-4" if x["round"] <= 4 else "R5-8" if x["round"] <= 8 else "R9-12"] += e
            else:
                bands["honest"] += e
            q = x["quarantined"]
            if q == g["rogue"]:
                out = True
            elif q:
                fq_after += out; fq_before += (not out)
        if not g["caught_round"]:
            k = sum(1 for x in g["transcript"] if g["rogue"] in x["answers"] and x["answers"][g["rogue"]]["answer"] != x["truth"])
            miss["never lied" if k == 0 else "lied once" if k == 1 else "lied 2+"] += 1
    return {"damage": {k: round(v / n, 1) for k, v in bands.items()}, "miss": miss,
            "fq_before": round(fq_before / n, 3), "fq_after": round(fq_after / n, 3)}


def compact(g):
    rounds = []
    for r in g["transcript"]:
        rounds.append({
            "r": r["round"], "truth": r["truth"], "team": round(r["team"], 1),
            "ans": {n: a["answer"] for n, a in r["answers"].items()},
            "ret": ({"n": r["retrial"]["name"], "a": r["retrial"]["answer"]} if r.get("retrial") else None),
            "ret2": ({"n": r["retrial2"]["name"], "a": r["retrial2"]["answer"]} if r.get("retrial2") else None),
            "q": r["quarantined"],
            "post": ({k: round(v, 4) for k, v in r["posterior"].items()} if r["posterior"] else None),
            "imp": {k: round(v, 1) for k, v in impacts(r).items()},
            "why": (r["log"] or {}).get("reason") if r["posterior"] else None,
        })
    return {"gid": g["gid"], "rogue": g["rogue"], "caught": g["caught_round"],
            "fq": g["false_quarantines"], "err": round(g["ledger_error"]), "rounds": rounds}


def main(out):
    data = {"seed": HELDOUT_SEED, "tau": TAU, "policies": {}}
    for pol in POLICY_ORDER:
        games = {}
        for label, fac, ret, rep in (("Baseline", Baseline, False, False),
                                     ("Prosecutor", lambda: ProsecutorV2(), True, "median"),
                                     ("V1", lambda: Prosecutor(tau=0.55), True, True)):
            full = [play(HELDOUT_SEED, i, fac, POLICIES[pol], ret, rep) for i in range(500)]
            s = summarize(full)
            games[label] = {"autopsy": autopsy(full), "summary": {k: (list(v) if isinstance(v, tuple) else v) for k, v in s.items()},
                            "games": ([compact(g) for g in full[:N_SHOW]] if label != "V1" else [])}
        data["policies"][pol] = games
    sweep = []
    for tau in (0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99):
        for pol in ("classic", "sneaky"):
            s = summarize([play(HELDOUT_SEED, i, lambda: ProsecutorV2(tau=tau), POLICIES[pol], True, "median") for i in range(300)])
            sweep.append({"tau": tau, "policy": pol, "catch": round(s["catch_rate"], 3), "fq": round(s["false_q"], 3)})
    for pol in ("classic", "sneaky"):
        s = summarize([play(HELDOUT_SEED, i, Baseline, POLICIES[pol], False) for i in range(300)])
        sweep.append({"tau": None, "policy": pol, "catch": round(s["catch_rate"], 3), "fq": round(s["false_q"], 3), "baseline": True})
    data["sweep"] = sweep
    import pathlib
    ln = pathlib.Path(out).parent / "length.json"
    if ln.exists():
        data["length"] = json.loads(ln.read_text())
    prog = pathlib.Path(out).parent / "progress.json"
    if prog.exists():
        data["progress"] = json.loads(prog.read_text())
    with open(out, "w") as f:
        json.dump(data, f, separators=(",", ":"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "dashboard/data.json")
