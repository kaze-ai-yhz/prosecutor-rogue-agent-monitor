# Experiments

> **Status: v3 is an experimental candidate, not the submitted system.** The headline system is still **Prosecutor v2** (see [RESULTS.md](../RESULTS.md) and [SYSTEM.md](../SYSTEM.md)). One independent audit re-ran every v3 held-out row, found them exact and found no rule violations, and recommended adoption *with the caveats below* (most importantly: catches happen later). The team has not decided to switch to v3; do not quote v3 numbers as the final result.

## v2 run outputs (`v2/`)

Raw rows behind the v2 tables in RESULTS.md: `report.jsonl` (Baseline / v1 / v2 on held-out seeds) and `ablate.jsonl` (v2 minus each component).

## v3 candidate (`v3/`, experimental)

`ProsecutorV3` (in `prosecutor/monitor.py`, appended after v2; v2 is unchanged) adds two flags on top of v2, both aimed at trust-then-strike rogues:

- **late_prior**: the change-point prior puts more weight on late switch rounds (proportional to k^cp_gamma) instead of uniform.
- **late_decision**: from round `late_from` on, the quarantine threshold drops to `late_tau`. A retrial-confirmed error is still required.

Params (`scripts/tuned_v3.json`, tuned on dev seed 1000 only): tau 0.8, mag_w 0.5, cp_weight 0.3, cp_gamma 3.0, late_tau 0.5, late_from 11. With both flags off, V3 reproduces v2 exactly (`python3 scripts/run_v3.py check`).

Held-out, n = 500 per row (caught · false quarantines/game · ledger error · extra calls/game):

| Rogue | Seed | Baseline | v2 | v3 (experimental) |
|---|---|---|---|---|
| classic | 2026 | 87.2% · 1.37 · 289 | 90.8% · 0.058 · 2.2 · 5.3 | 91.6% · 0.042 · 2.3 · 5.5 |
| sneaky | 2026 | 67.8% · 1.09 · 74 | 66.6% · 0.078 · 8.2 · 5.2 | 74.8% · 0.084 · 8.4 · 5.4 |
| honest-shaped | 2026 | 78.8% · 1.22 · 64 | 72.2% · 0.110 · 4.2 · 5.7 | 74.8% · 0.112 · 5.1 · 5.9 |
| late-big | 2026 | 59.0% · 1.03 · 160 | 57.0% · 0.222 · 2.3 · 5.0 | 67.8% · 0.200 · 2.3 · 5.1 |
| framer | 2026 | 63.0% · 1.05 · 90 | 67.2% · 0.074 · 5.8 · 4.9 | 71.0% · 0.092 · 6.0 · 5.0 |
| classic | 7777 | 88.0% · 1.37 · 295 | 90.2% · 0.070 · 2.8 · 5.3 | 90.8% · 0.048 · 3.1 · 5.6 |
| sneaky | 7777 | 69.6% · 1.17 · 76 | 72.0% · 0.106 · 8.6 · 5.4 | 76.6% · 0.084 · 9.1 · 5.6 |
| honest-shaped | 7777 | 83.4% · 1.32 · 68 | 74.6% · 0.116 · 4.5 · 5.7 | 77.4% · 0.086 · 5.1 · 6.0 |
| late-big | 7777 | 59.0% · 1.02 · 162 | 60.0% · 0.212 · 2.5 · 5.1 | 68.8% · 0.206 · 2.5 · 5.1 |
| framer | 7777 | 65.4% · 1.14 · 94 | 66.8% · 0.088 · 6.8 · 5.0 | 69.6% · 0.080 · 7.2 · 5.2 |

Raw rows: `v3/runs/report.jsonl`, ablation `v3/runs/ablate.jsonl`, dev tuning `v3/runs/tune.jsonl`, identity check `v3/runs/check100.jsonl`.

**Caveats, read before citing:**

- **Catches happen later.** Median catch round rises (seed 2026: sneaky 9 to 11, framer 5.5 to 9, honest-shaped 6 to 8, classic 4 to 5). Much of the catch gain comes from the lowered threshold in round 11 and later, so catch % overstates how much detection improves. Ledger error stays roughly flat.
- The chosen params sit at the edge of the tuning grid (tau 0.8, cp_gamma 3), and win on dev by a small margin (80.4 vs 79.9 mean catch for the runner-up). The grid had 52 valid configs, not 56 as first reported.
- False quarantines get slightly worse in a few cells (framer 2026: 0.074 to 0.092).

- The late-strike direction was chosen *after* seeing v2's weak sneaky and late-big numbers on the held-out seed, so late-big is no longer a fully clean held-back test. Seed 7777 shows the same pattern, which helps, but a fresh seed would be the honest check.
- The ablation says `late_decision` does most of the work; `late_prior` adds little (removing it: classic 91.6%, sneaky 75.6%, late-big 67.6%).
- Dev-seed gains were within noise; the held-out gains are larger than dev, which is a reason for suspicion, not confidence.
- honest-shaped is still below baseline catch rate (74.8% vs 78.8%), as in v2.
- About 0.1 to 0.3 more extra calls per game than v2.

Reproduce: `python3 scripts/run_v3.py report 500 && python3 scripts/run_v3.py ablate 500`.

### Other v3 directions tried (not adopted)

| Direction | Idea | Outcome |
|---|---|---|
| late (became v3) | Late-weighted change-point prior + lower late threshold | Verified, combined into v3 above |
| rates | Marginalize per-agent honest and rogue error rates instead of fixed rates | Rejected by verifier: lower catch than v2 in 9 of 10 held-out cells |
| gate | Skip the second retrial when the first verdict is decisive, to save calls | Rejected: saves only 0.25 to 0.45 calls/game and catch is at or slightly below v2 |
| tune | Joint re-tune of all v2 weights | Run failed, no result |
