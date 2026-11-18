#!/usr/bin/env bash
# Fresh-machine setup for the Track 2 kit, from public sources only:
#   1. checks git, curl and Python 3.10+
#   2. clones the public starter and writes the organizer's original sim.py
#      (starter commit af7271b, checksum verified) to game/sim.py, plus
#      game/sim_live.py, a copy whose real-mode call works on current models
#   3. creates .venv with the Anthropic Python SDK
#   4. optionally downloads one Among Us log file (Hugging Face, pinned
#      revision, checksum verified) to data/amongus/
#   5. runs the mock baseline and checks it reproduces 177/200 and 1.38
# Safe to re-run. Writes nothing outside this kit folder.
#
# Usage: scaffold/bootstrap.sh [--with-amongus] [--skip-venv]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STARTER="${STARTER_DIR:-$ROOT/trust-safety-impact-lab}"
STARTER_URL="https://github.com/sergeicu/trust-safety-impact-lab.git"
SIM_COMMIT="af7271b3e9212ce7cb63b06bd9b38ec97ddfa2ca"
SIM_SHA256="ca50b8a28fab0a9cb2380ce2587784b166bb4966eecbff342a722a981e33cd43"
AMONGUS_REV="a5ff310ffa9f780b019716f1f4d9a1e1db283ccb"
AMONGUS_PATH="expt-logs/2025-02-01_llama_llama_100_games_v3/agent-logs-compact.json"
AMONGUS_SHA256="5120084bb54b79e9387f30d7475f7bf5b4d0d479eae477aa6f33279c8e7b2c7c"
AMONGUS_DEST="$ROOT/data/amongus/llama_llama-agent-logs-compact.json"
ANTHROPIC_PIN="${ANTHROPIC_PIN:-anthropic==2.4.0}"

WITH_AMONGUS=0
SKIP_VENV=0
for arg in "$@"; do
  case "$arg" in
    --with-amongus) WITH_AMONGUS=1 ;;
    --skip-venv) SKIP_VENV=1 ;;
    -h|--help) sed -n '2,14p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

say() { printf '\n== %s\n' "$*"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  else shasum -a 256 "$1" | awk '{print $1}'; fi
}

say "1/5 Prerequisites"
command -v git >/dev/null 2>&1 || die "git is missing"
command -v curl >/dev/null 2>&1 || die "curl is missing"
PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || die "python3 is missing"
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || die "Python 3.10+ is required (anthropic 2.x needs it); found $("$PY" -V 2>&1)"
echo "git, curl and $("$PY" -V 2>&1) found"

say "2/5 Public starter and the original sim"
if [[ ! -d "$STARTER/.git" ]]; then
  git clone --quiet "$STARTER_URL" "$STARTER"
fi
if ! git -C "$STARTER" cat-file -e "${SIM_COMMIT}^{commit}" 2>/dev/null; then
  git -C "$STARTER" fetch --quiet --unshallow 2>/dev/null || git -C "$STARTER" fetch --quiet origin
fi
mkdir -p "$ROOT/game"
git -C "$STARTER" show "${SIM_COMMIT}:starters/rogue_agent/sim.py" > "$ROOT/game/sim.py"
[[ "$(sha256_of "$ROOT/game/sim.py")" == "$SIM_SHA256" ]] || die "game/sim.py checksum mismatch"
echo "game/sim.py written from starter commit ${SIM_COMMIT:0:7}, checksum OK"

# sim_live.py: same game; the real-mode call reads the first text block (current
# models can return a thinking block first), allows 1024 output tokens instead
# of 150, and sends output_config.effort from SIM_EFFORT (default low; set
# SIM_EFFORT= to omit it for models without effort support).
"$PY" - "$ROOT/game/sim.py" "$ROOT/game/sim_live.py" <<'PATCH'
import sys
src, dst = sys.argv[1], sys.argv[2]
code = open(src).read()
edits = [
    ("    msg = client.messages.create(model=model, max_tokens=150,\n",
     "    effort = os.environ.get(\"SIM_EFFORT\", \"low\")\n"
     "    extra = {\"output_config\": {\"effort\": effort}} if effort else {}\n"
     "    msg = client.messages.create(model=model, max_tokens=1024, **extra,\n"),
    ("    text = msg.content[0].text\n",
     "    text = next((b.text for b in msg.content if b.type == \"text\"), \"\")\n"),
]
for old, new in edits:
    if code.count(old) != 1:
        sys.exit("sim_live patch: expected exactly one match for %r" % old.strip())
    code = code.replace(old, new)
open(dst, "w").write(code)
PATCH
echo "game/sim_live.py written (real-mode fixes only; mock mode unchanged)"

say "3/5 Python environment"
PYRUN="$PY"
SDK_OK=0
VENV_PY="$ROOT/.venv/bin/python"
if [[ $SKIP_VENV -eq 1 ]]; then
  echo "skipped (--skip-venv); using $PY"
else
  # A venv without pip (for example a failed earlier attempt) is rebuilt.
  if [[ -x "$VENV_PY" ]] && ! "$VENV_PY" -m pip --version >/dev/null 2>&1 && ! command -v uv >/dev/null 2>&1; then
    rm -rf "$ROOT/.venv"
  fi
  if [[ ! -x "$VENV_PY" ]]; then
    "$PY" -m venv "$ROOT/.venv" >/dev/null 2>&1 \
      || { rm -rf "$ROOT/.venv"; command -v uv >/dev/null 2>&1 && uv venv --quiet --python "$PY" "$ROOT/.venv"; } \
      || true
  fi
  if [[ -x "$VENV_PY" ]]; then
    if "$VENV_PY" -m pip --version >/dev/null 2>&1; then
      "$VENV_PY" -m pip install --quiet --disable-pip-version-check "$ANTHROPIC_PIN" && SDK_OK=1
    elif command -v uv >/dev/null 2>&1; then
      uv pip install --quiet --python "$VENV_PY" "$ANTHROPIC_PIN" && SDK_OK=1
    fi
  fi
  if [[ $SDK_OK -eq 1 ]]; then
    PYRUN="$VENV_PY"
    echo ".venv ready: $("$PYRUN" -c 'import anthropic; print("anthropic", anthropic.__version__)')"
  else
    echo "WARNING: could not build .venv with the Anthropic SDK. Mock mode still works."
    echo "  Debian/Ubuntu: sudo apt-get install -y python3-venv, then re-run."
    echo "  Or install uv (https://docs.astral.sh/uv/) and re-run, or set PYTHON to another Python 3.10+."
  fi
fi

say "4/5 Among Us logs (optional)"
if [[ $WITH_AMONGUS -eq 1 ]]; then
  mkdir -p "$(dirname "$AMONGUS_DEST")"
  if [[ ! -f "$AMONGUS_DEST" || "$(sha256_of "$AMONGUS_DEST")" != "$AMONGUS_SHA256" ]]; then
    curl -fsSL --retry 3 -o "$AMONGUS_DEST.part" \
      "https://huggingface.co/datasets/7vik/amongus/resolve/${AMONGUS_REV}/${AMONGUS_PATH}"
    mv "$AMONGUS_DEST.part" "$AMONGUS_DEST"
  fi
  [[ "$(sha256_of "$AMONGUS_DEST")" == "$AMONGUS_SHA256" ]] || die "Among Us file checksum mismatch"
  echo "data/amongus/llama_llama-agent-logs-compact.json (63.5 MB), checksum OK"
else
  echo "skipped (re-run with --with-amongus)"
fi

say "5/5 Smoke test: mock baseline"
OUT="$("$PYRUN" "$ROOT/game/sim.py" --mock --games 200 --seed 0)"
echo "$OUT"
grep -q "177/200" <<<"$OUT" && grep -q "1.38" <<<"$OUT" \
  || die "baseline differs from the expected 177/200 caught and 1.38 false quarantines per game"
OUT_LIVE="$("$PYRUN" "$ROOT/game/sim_live.py" --mock --games 200 --seed 0)"
[[ "$OUT" == "$OUT_LIVE" ]] || die "game/sim_live.py mock output differs from game/sim.py"
echo
echo "Bootstrap complete. Next: export ANTHROPIC_API_KEY for live games (optional)."
