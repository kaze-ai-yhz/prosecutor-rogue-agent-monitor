# Independent replication on a fresh seed

Run by a second team member on a second machine, with a seed the team never used for tuning or reporting (31337; dev was 1000, held-out was 2026). Same harness and rules as `RESULTS.md`, n = 300 games per row.

```bash
python3 scripts/fresh_seed.py . 31337 300
```

| Rogue | Monitor | Rogue caught | Median round | False quarantines/game | Mean ledger error | Extra calls/game |
|---|---|---|---|---|---|---|
| classic | Baseline | 265/300 (88.3%, CI 84–91) | 6 | 1.38 | 310.7 | 0 |
| classic | Prosecutor v2 | 282/300 (94.0%, CI 91–96) | 4 | 0.08 | 2.4 | 5.3 |
| sneaky | Baseline | 205/300 (68.3%, CI 63–73) | 9 | 1.10 | 74.1 | 0 |
| sneaky | Prosecutor v2 | 204/300 (68.0%, CI 63–73) | 9 | 0.11 | 8.6 | 5.2 |
| honest-shaped | Baseline | 248/300 (82.7%, CI 78–87) | 7 | 1.30 | 70.1 | 0 |
| honest-shaped | Prosecutor v2 | 235/300 (78.3%, CI 73–83) | 6 | 0.12 | 4.0 | 5.7 |
| late-big | Baseline | 165/300 (55.0%, CI 49–61) | 10 | 0.96 | 156.1 | 0 |
| late-big | Prosecutor v2 | 153/300 (51.0%, CI 45–57) | 10 | 0.19 | 2.4 | 4.7 |
| framer | Baseline | 194/300 (64.7%, CI 59–70) | 7 | 1.09 | 95.6 | 0 |
| framer | Prosecutor v2 | 190/300 (63.3%, CI 58–69) | 5 | 0.10 | 7.0 | 4.9 |

**What replicates.** Prosecutor v2 removes about one tenth as many honest agents (0.08–0.19 per game against 0.96–1.38) and keeps the ledger far closer to the truth on every rogue. On the starter's classic rogue it also catches more (94.0% against 88.3%).

**What does not.** The catch-rate lead on the framer rogue seen on the held-out seed (67.2% against 63.0%) is not there on this seed (63.3% against 64.7%, inside the confidence interval). Against the honest-shaped and late-big rogues v2 catches less often than the baseline here too. The honest summary is a trade: far fewer false accusations and a protected ledger, at an equal or lower catch rate against rogues that hide.
