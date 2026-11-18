#!/usr/bin/env python3
"""Autopsy of the organizer's baseline monitor (analysis only, no new monitor).

Replays the original mock games (seed 0) with baseline_monitor and reports
where its false quarantines and ledger damage come from, plus two ways the
mock leaks the answer (items in the transcript, the rogue's unique note).

Usage: python3 scaffold/scripts/baseline_autopsy.py [path/to/sim.py] [games]
Defaults: game/sim.py (written by scaffold/run.sh) and 200 games.
"""
import collections
import importlib.util
import random
import sys

SIM_PATH = sys.argv[1] if len(sys.argv) > 1 else "game/sim.py"
spec = importlib.util.spec_from_file_location("sim", SIM_PATH)
sim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sim)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200

rng = random.Random(0)
agent_fn = lambda name, is_rogue, values, truth, history: sim.mock_agent(rng, truth, is_rogue)

fq_post = fq_pre = fq_partner_strikes = fq_slip_strikes = 0
err_rogue = err_other = err_after_catch = err_uncaught = 0.0
rogue_notes, honest_notes = collections.Counter(), collections.Counter()
rogue_assign = rogue_wrong = honest_assign = honest_wrong = 0
offsets_rogue, offsets_honest = collections.Counter(), collections.Counter()
rounds_total = disagree_rounds = leak_rounds = late_rogue_wrong = 0
uncaught_rogue_assignments = []
rogue_quarantine_rounds = []

for g in range(N):
    log = []

    def mon(t, active):
        s = sim.baseline_monitor(t, active)
        log.append((t[-1]["round"], s))
        return s

    res = sim.play(rng, mon, agent_fn)
    rogue, caught = res["rogue"], res["caught_round"]
    if not caught:
        uncaught_rogue_assignments.append(sum(1 for r in res["transcript"] if rogue in r["answers"]))
    for r in res["transcript"]:
        truth = sum(r["items"])
        rounds_total += 1
        leak_rounds += 1  # sum(items) is always the true total
        ans = r["answers"]
        if len({a["answer"] for a in ans.values()}) > 1:
            disagree_rounds += 1
        for name, a in ans.items():
            off = a["answer"] - truth
            if name == rogue:
                rogue_assign += 1
                rogue_notes[a["note"]] += 1
                if off:
                    rogue_wrong += 1
                    offsets_rogue[off] += 1
                    if r["round"] >= 10:
                        late_rogue_wrong += 1
            else:
                honest_assign += 1
                honest_notes[a["note"]] += 1
                if off:
                    honest_wrong += 1
                    offsets_honest[off] += 1
        e = abs(r["team"] - truth)
        if rogue in ans and ans[rogue]["answer"] != truth:
            err_rogue += e
        else:
            err_other += e
        if caught and r["round"] > caught:
            err_after_catch += e
        if not caught:
            err_uncaught += e
    for rnd, s in log:
        if s and s != rogue:
            if caught and rnd > caught:
                fq_post += 1
            else:
                fq_pre += 1
            for r in res["transcript"][:rnd]:
                ans = r["answers"]
                if s in ans and len({a["answer"] for a in ans.values()}) > 1:
                    if rogue in ans:
                        fq_partner_strikes += 1
                    else:
                        fq_slip_strikes += 1

print(f"games={N} rounds={rounds_total} disagreement rounds={disagree_rounds}")
print(f"false quarantines total={fq_pre + fq_post} ({(fq_pre + fq_post) / N:.2f}/game): "
      f"after rogue already caught={fq_post}, before={fq_pre}")
print(f"strikes held by wrongly quarantined agents: from a disagreement with the rogue={fq_partner_strikes}, "
      f"from honest slips={fq_slip_strikes}")
print(f"rogue: assigned {rogue_assign}x, wrong {rogue_wrong}x ({rogue_wrong / rogue_assign:.0%}); offsets {dict(offsets_rogue)}")
print(f"honest: assigned {honest_assign}x, wrong {honest_wrong}x ({honest_wrong / honest_assign:.1%}); offsets {dict(offsets_honest)}")
print(f"notes written by rogue: {dict(rogue_notes)}")
print(f"notes written by honest agents: {dict(honest_notes)}")
tot = err_rogue + err_other
print(f"ledger error total={tot:.0f}: rounds with a wrong rogue answer={err_rogue:.0f} ({err_rogue / tot:.0%}), other={err_other:.0f}")
print(f"ledger error from never-caught games={err_uncaught:.0f} ({err_uncaught / tot:.0%}); after the catch={err_after_catch:.0f}")
print(f"uncaught games={len(uncaught_rogue_assignments)}; rogue assignments in them={uncaught_rogue_assignments}")
print(f"rounds where the monitor could recompute the truth from 'items': {leak_rounds}/{rounds_total}")
print(f"rogue wrong answers in rounds 10-12: {late_rogue_wrong}")
