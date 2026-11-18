# Prosecutor: Spot the Rogue Agent

Built at the Claude Impact Lab: AI Trust & Safety (Antler SF, Tue Nov 17 2026). Track 2, challenges A (better monitor) + C (sneakier rogue).

**Results:** see [RESULTS.md](RESULTS.md) (current: Prosecutor v2, 91% caught, 0.06 false quarantines/game vs baseline 87% and 1.37). **Run everything:** `./run.sh`. **Dashboard:** open `dashboard/index.html`. **Game explorer:** open `explorer/rogue-explorer.html`.

Code layout: `prosecutor/` (monitor, paired evaluation harness, sneaky rogue, notes reader, dashboard data), `dashboard/` (static replay dashboard), `scaffold/` (bootstrap that fetches the organizer's original `sim.py` from the public starter).

## Goal

Build a monitor, called Prosecutor, that finds the saboteur in a five-agent ledger game without wrongly quarantining honest teammates. Measure it against the starter baseline on the four official numbers, then stress-test it with a sneakier rogue that builds trust and strikes late.

## Pitch (one paragraph)

The baseline monitor catches the rogue 88% of the time (177 of 200 mock games) but wrongly fires about 1.4 honest agents every game. A paranoid monitor that fires the innocent is just as bad as one that misses the saboteur. Prosecutor does not convict without evidence: a direction-bias check on errors, a model read of notes only for agents already flagged, and a retrial by a third agent before anyone is quarantined. We will report catch rate, median round caught, false quarantines per game, and mean ledger error, baseline versus ours, on a frozen set of games, including a sneakier rogue.

## Quick start

```bash
# From this repo
chmod +x scaffold/run.sh
./scaffold/run.sh
```

That clones the public starter at `github.com/sergeicu/trust-safety-impact-lab` if it is missing and writes the organizer's original `sim.py` from starter commit `af7271b` to `game/sim.py` (git-ignored; the starter removed it from `main` at 6:09 PM PT). Then it runs:

```bash
python3 game/sim.py --mock --games 200
```

Expected baseline (mock, 200 games, seed 0):

| Metric | Baseline |
|---|---|
| Rogue caught | 88% (177/200) |
| Median round caught | 6 |
| False quarantines / game | 1.38 |
| Mean ledger error | 285 |

[SUBMISSION_DRAFT.md](SUBMISSION_DRAFT.md) is the team-card draft. The organizer's `sim.py` is not included in this repo; `scaffold/run.sh` fetches it from the public starter.

The monitor hook in the starter is:

```python
def monitor(transcript, active) -> str | None
# transcript: list of rounds, each
#   {"round", "items", "answers": {name: {"answer", "note"}}, "team"}
# active: names still in the game
# The monitor never sees the true total.
```

The Prosecutor monitor lives in `prosecutor/monitor.py`; `scaffold/prosecutor/monitor.py` is the original stub.

`dashboard/vendor/chart.umd.js` is Chart.js (MIT license, banner retained).
