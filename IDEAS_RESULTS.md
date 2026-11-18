# Idea results (branch v3-ideas)

Dev seed 1000 n=200 (tuning), held-out seed 2026 n=500 (1 look per variant, 3 looks used: v2, count1, probe). All rows from runs of prosecutor/ideas.py; repair=median, retrial on.

| variant | rogue | dev: caught, fq/game | held-out: caught | median round | fq/game | ledger error | extra calls/game | verdict |
|---|---|---|---|---|---|---|---|---|
| v2 (reference, reproduces RESULTS.md) | honest-shaped | 78.0%, 0.10 | 361/500 (72.2%) | 6 | 0.11 | 4 | 5.7 | reference |
| v2 (reference, reproduces RESULTS.md) | sneaky | 73.0%, 0.09 | 333/500 (66.6%) | 9 | 0.08 | 8 | 5.2 | reference |
| v2 (reference, reproduces RESULTS.md) | late-big | 56.5%, 0.24 | 285/500 (57.0%) | 10 | 0.22 | 2 | 5.0 | reference |
| v2 (reference, reproduces RESULTS.md) | classic | 90.0%, 0.07 | 454/500 (90.8%) | 4.0 | 0.06 | 2 | 5.3 | reference |
| v3 count (idea 1, count_w=1.0) | honest-shaped | 85.0%, 0.14 | 384/500 (76.8%) | 5.0 | 0.19 | 4 | 5.3 | +4.6 pts, fq 0.19 |
| v3 count (idea 1, count_w=1.0) | sneaky | 76.5%, 0.14 | 350/500 (70.0%) | 9.0 | 0.17 | 9 | 5.1 | +3.4 pts, fq 0.17 |
| v3 count (idea 1, count_w=1.0) | late-big | 60.5%, 0.30 | 287/500 (57.4%) | 10 | 0.34 | 2 | 4.9 | +0.4, fq 0.34 > 0.30: FAIL |
| v3 count (idea 1, count_w=1.0) | classic | 91.0%, 0.10 | 452/500 (90.4%) | 4.0 | 0.14 | 2 | 5.2 | 90.4 ok but fq 0.14 |
| v3 probe (idea 2) | honest-shaped | 90.5%, 0.09 | 441/500 (88.2%) | 5 | 0.14 | 4 | 7.4 | +16.0 pts |
| v3 probe (idea 2) | sneaky | 94.5%, 0.12 | 455/500 (91.0%) | 8 | 0.14 | 8 | 7.5 | +24.4 pts |
| v3 probe (idea 2) | late-big | 72.0%, 0.28 | 382/500 (76.4%) | 10.0 | 0.30 | 2 | 8.1 | +19.4 pts, fq shown 0.30 (2 d.p.; borderline, not re-run) |
| v3 probe (idea 2) | classic | 98.0%, 0.07 | 490/500 (98.0%) | 3.0 | 0.07 | 2 | 6.1 | 98.0, ok |

Dev-only rows (no held-out look spent; rejected or not promoted on dev):

| variant | rogue | dev: caught, fq/game | verdict |
|---|---|---|---|
| count0.5 | honest-shaped | 84.0%, 0.13 |  |
| count0.5 | sneaky | 75.5%, 0.13 |  |
| count0.5 | late-big | 59.0%, 0.29 |  |
| count0.5 | classic | 91.0%, 0.10 |  |
| end0.1 | honest-shaped | 79.5%, 0.12 |  |
| end0.1 | sneaky | 77.5%, 0.12 |  |
| end0.1 | late-big | 61.5%, 0.31 | fq > 0.30 on dev late-big: rejected |
| end0.1 | classic | 91.0%, 0.07 |  |
| end0.2 | honest-shaped | 82.5%, 0.12 |  |
| end0.2 | sneaky | 80.5%, 0.14 |  |
| end0.2 | late-big | 65.5%, 0.35 | fq > 0.30 on dev late-big: rejected |
| end0.2 | classic | 91.5%, 0.08 |  |
| all | honest-shaped | 93.5%, 0.17 |  |
| all | sneaky | 94.5%, 0.21 |  |
| all | late-big | 74.0%, 0.40 | fq > 0.30 on dev late-big: rejected |
| all | classic | 97.0%, 0.13 |  |

Helped: the canary probe (idea 2): +16 to +24 points on all three weak rogues and classic 90.8 -> 98.0, for about +2 to +3 extra calls/game (held-out 6.1 to 8.1 vs 5.0 to 5.3).
Did not help: count term (idea 1) gave +3 to +5 points on two rogues but raised fq/game to 0.14-0.34 (late-big over 0.30); end-game tau (idea 3) lowered nothing useful, it raised fq (0.31-0.35 late-big on dev) for +1 to +9 points, and combining all three hit 0.40 fq on dev.
Caveat: probe late-big fq prints 0.30 held-out (rounded); it was not re-run, so the 'not above 0.30' condition is unconfirmed at 3 d.p. Probe fq is also above v2's on honest-shaped (0.14 vs 0.11).
