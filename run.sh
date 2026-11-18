#!/usr/bin/env bash
# One command: fetch the organizer's original sim if missing, reproduce the official baseline,
# run baseline vs Prosecutor on frozen held-out games (normal + sneaky rogues), rebuild the dashboard.
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -f game/sim.py ]]; then ./scaffold/run.sh >/dev/null; fi
echo "== Official baseline (organizer sim, mock, 200 games, seed 0)"
python3 game/sim.py --mock --games 200 --seed 0
echo; echo "== Held-out comparison"
python3 -m prosecutor.evaluate --games "${GAMES:-500}"
python3 -m prosecutor.dashboard_data dashboard/data.json
python3 dashboard/build.py
echo "Open dashboard/index.html"
