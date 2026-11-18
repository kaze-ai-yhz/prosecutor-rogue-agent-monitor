# Prosecutor: results

All numbers: held-out seed 2026, n = 500 paired games per row (same rogue, items and agent behaviour for every monitor), mock agents from the organizer's original sim (starter commit af7271b). The monitor never sees `items` or the true total; mock notes come from one shared pool. Thresholds and weights were tuned only on dev seed 1000 with the classic, sneaky and honest-shaped rogues. `late-big` and `framer` are held-back rogues nobody tuned on. A fresh seed (7777) was checked too.

Official baseline reproduced exactly (organizer sim, seed 0, 200 games): 177/200 caught (88%), median round 6, 1.38 false quarantines/game, ledger error 285.

## Milestone log

| Step | Finding | Change |
|---|---|---|
| v1 | 60% of baseline false quarantines happen after the rogue is out; bystanders pay like culprits | One probability over five suspects, agreements clear, third-agent retrial before quarantine, error direction, stand-down after a catch |
| v1.1 | 92% of damage comes from rounds where the rogue lied | Repair: a 2-of-3 retrial majority replaces the average |
| v1.2 | Risk of tuning to our own rogues | Two held-back rogues: late big strikes, framer |
| v1.3 | Game length (idea from the Rogue Agent Explorer) | Baseline false quarantines rise to 3.0/game at 48 rounds; Prosecutor stays 0.2–0.44 |
| v2a–e | Five fixes from the damage autopsy, each independently re-run and audited | Error size, anti-framing second retrial, recency (change-point), median commit, interrogate |
| **v2** | Each fix helps a different rogue | **ProsecutorV2 = error size + anti-framing + recency, ledger commits the median of all answers.** τ = 0.7, mag_w = 0.5, cp_weight = 0.3 |

## Prosecutor v2 vs v1 vs baseline (caught · median round · false quarantines/game · ledger error · extra calls/game)

| Rogue | Baseline | Prosecutor v1 + repair | **Prosecutor v2** |
|---|---|---|---|
| classic | 87.2% · R6 · 1.37 · 289 · 0 | 89.0% · R4 · 0.24 · 30 · 2.9 | **90.8% · R4 · 0.06 · 2.2 · 5.3** |
| sneaky | 67.8% · R9 · 1.09 · 74 · 0 | 58.8% · R9 · 0.41 · 21 · 2.9 | 66.6% · R9 · **0.08** · 8.2 · 5.2 |
| honest-shaped | 78.8% · R7 · 1.22 · 64 · 0 | 80.6% · R4 · 0.28 · 10 · 2.8 | 72.2% · R6 · **0.11** · 4.2 · 5.7 |
| late-big (held back) | 59.0% · R10 · 1.03 · 160 · 0 | 43.2% · R10 · 0.47 · 25 · 2.7 | 57.0% · R10 · **0.22** · 2.3 · 5.0 |
| framer (held back) | 63.0% · R8 · 1.05 · 90 · 0 | 57.8% · R4 · 0.35 · 17 · 2.7 | **67.2%** · R5.5 · **0.07** · 5.8 · 4.9 |

Fresh seed 7777 points the same way (classic 90.2% / 0.07, sneaky 72.0% / 0.11, late-big 60.0%).

**Headline:** against the starter rogue, v2 catches 91% (baseline 87%) and wrongly removes 0.06 honest agents per game (baseline 1.37, 24× fewer). The books end 2 off on average (baseline 289).

**Ablation (held-out):** without error size, classic drops to 84.8% and late-big to 39.2%. Without anti-framing, sneaky drops to 52% and framer to 52.6%. Without recency, false quarantines rise by about half. Without median commit, detection is identical but ledger error returns to about 31 on classic (most of the ledger gain is this protocol change, not the monitor).

**Honest limitations**
- Sneaky and late-big rogues are caught about as often as by the trigger-happy baseline, not more, but with 5–14× fewer innocents fired.
- v2 catches fewer honest-shaped rogues (small, two-sided errors) than the baseline: 72% vs 79%.
- v2 spends about 5 extra agent calls per game (two retrials on each disputed item) against 2.8 for v1.
- The tuned τ = 0.7 sits at the top edge of the searched grid; a wider search may do better.
- The note-reading check on real Among Us logs (`prosecutor/amongus.py`) is not run yet: it needs the Hugging Face file and an API key.

Reproduce: `./run.sh` (table and dashboard), `python3 scripts/run_v2.py report 500` and `python3 scripts/run_v2.py ablate 500` (v2 rows and ablation).
