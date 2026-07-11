#!/bin/sh
# Track 1 self-review gate: the Track 2 review agent judges the Track 1 paper.
# Reuses scripts/event_review.sh (credentials, provider, degraded/verdict/guard
# hard-gate), then additionally requires overall_recommendation >= min-rec.
#
# Usage: bash scripts/track1_selfreview.sh <paper.md> <run-id> [min-rec=3]
set -eu

if [ $# -lt 2 ] || [ $# -gt 3 ]; then
  echo "usage: bash scripts/track1_selfreview.sh <paper.md> <run-id> [min-rec]" >&2
  exit 2
fi
MIN_REC=${3:-3}

bash scripts/event_review.sh "$1" "$2"

PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python

"$PY" - "$2" "$MIN_REC" <<'EOF'
import json, sys

run_id, min_rec = sys.argv[1], int(sys.argv[2])
card = json.load(open(f"runs/{run_id}/review_scorecard.json"))
rec = card.get("overall_recommendation")
if not isinstance(rec, int) or rec < min_rec:
    print(f"TRACK1 SELFREVIEW GATE FAIL: overall_recommendation={rec} < required {min_rec}")
    sys.exit(1)
print(f"TRACK1 SELFREVIEW GATE PASS: rec={rec} (>= {min_rec})")
EOF
