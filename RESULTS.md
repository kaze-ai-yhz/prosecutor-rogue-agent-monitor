# Prosecutor: results

Held-out: seed 2026, games 0..499 (hash 58d99cd075d3), n = 500 paired games per row. Threshold τ = 0.55 chosen on dev seed 1000 only. Mock agents from the organizer's original sim (starter commit af7271b); the monitor never sees `items` or the true total; notes come from one shared pool. Reproduce with `./run.sh`.

Official baseline reproduced exactly (organizer sim, seed 0, 200 games): 177/200 caught (88%), median round 6, 1.38 false quarantines/game, ledger error 285.

| Rogue | Monitor | Rogue caught | Median round | False quarantines/game | Mean ledger error | Extra calls/game |
|---|---|---|---|---|---|---|
| classic | Baseline | 436/500 (87%, CI 84–90) | 6 | 1.37 (1.27–1.46) | 289 | 0 |
| classic | Prosecutor (no retrial) | 388/500 (78%) | 5 | 0.28 | 301 | 0 |
| classic | **Prosecutor** | **445/500 (89%, CI 86–91)** | **4** | **0.24 (0.21–0.28)** | 224 | 2.9 |
| classic | **Prosecutor + repair** | 445/500 (89%) | 4 | 0.24 | **30** | 2.9 |
| sneaky | Baseline | 339/500 (68%) | 9 | 1.09 | 74 | 0 |
| sneaky | Prosecutor | 294/500 (59%) | 9 | 0.41 | 81 | 2.9 |
| sneaky | Prosecutor + repair | 294/500 (59%) | 9 | 0.41 | 21 | 2.9 |
| honest-shaped | Baseline | 394/500 (79%) | 7 | 1.22 | 64 | 0 |
| honest-shaped | Prosecutor + repair | 403/500 (81%) | 4 | 0.28 | 10 | 2.8 |

**Headline:** on the starter's rogue, Prosecutor keeps the catch rate (89% vs 87%), catches it two rounds earlier, and cuts false quarantines from 1.37 to 0.24 per game (5.7× fewer). With the 2-of-3 repair the ledger error falls from 289 to 30.

**How it works:** one probability over five suspects (exactly one rogue), updated by agreements (exonerate), disagreements across different partners (triangulate), and the direction of retrial-confirmed errors. A third agent, the one trusted most, redoes every disputed item. Nobody is quarantined below τ or without at least one retrial-confirmed error. Claude's read of notes (`prosecutor/notes.py`) only nudges an already-flagged agent by at most ±0.4 nats. The retrial is the step that matters: without it, catch rate drops to 78%.

**Honest limitation:** the sneaky rogue (honest for its first two assignments, then mid-sized strikes on late or high-value rounds, and it frames honest agents when it is the retrial agent) gets caught less by Prosecutor (59%) than by the trigger-happy baseline (68%), although Prosecutor still fires 2.7× fewer innocents. Detection after the fact cannot undo late strikes; the repair (2-of-3 majority) is what protects the books (ledger error 21 vs 74).

**Not done yet:** the Among Us note-reading check (`prosecutor/amongus.py`) needs the Hugging Face file and an API key; neither was reachable from the build machine.
