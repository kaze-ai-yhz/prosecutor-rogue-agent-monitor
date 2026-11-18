#!/usr/bin/env bash
# Generic kickoff runner: fetch the organizer's original game, then run the
# official baseline in mock mode. This does not run Prosecutor. The monitor
# itself is written in the room during the build window.
#
# The organizer flattened the public starter at 6:09 PM PT on Nov 17, 2026 and
# removed starters/rogue_agent/sim.py from main. Commit af7271b is the last one
# that ships it, so the game is read from that commit and written to game/sim.py
# (git-ignored). The starter clone itself stays on main, so the track files and
# SUBMISSION.md you read are the current ones.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STARTER="${STARTER_DIR:-$ROOT/trust-safety-impact-lab}"
REPO_URL="https://github.com/sergeicu/trust-safety-impact-lab.git"
SIM_COMMIT="${SIM_COMMIT:-af7271b3e9212ce7cb63b06bd9b38ec97ddfa2ca}"
SIM="$ROOT/game/sim.py"
GAMES="${GAMES:-200}"
SEED="${SEED:-0}"

if [[ ! -d "$STARTER/.git" ]]; then
  echo "Cloning public starter into $STARTER"
  git clone --quiet "$REPO_URL" "$STARTER"
fi

if [[ ! -f "$SIM" ]]; then
  if ! git -C "$STARTER" cat-file -e "${SIM_COMMIT}^{commit}" 2>/dev/null; then
    echo "Fetching starter history to reach the original sim (commit ${SIM_COMMIT:0:7})"
    git -C "$STARTER" fetch --quiet --unshallow 2>/dev/null || git -C "$STARTER" fetch --quiet origin
  fi
  mkdir -p "$ROOT/game"
  git -C "$STARTER" show "${SIM_COMMIT}:starters/rogue_agent/sim.py" > "$SIM"
  echo "Wrote the organizer's original sim.py (commit ${SIM_COMMIT:0:7}) to game/sim.py"
fi

echo "Running official baseline: sim.py --mock --games $GAMES --seed $SEED"
echo "Monitor hook is baseline_monitor(transcript, active) in game/sim.py."
echo "To swap in Prosecutor later, point the sim at scaffold/prosecutor/monitor.py."
echo

python3 "$SIM" --mock --games "$GAMES" --seed "$SEED"
