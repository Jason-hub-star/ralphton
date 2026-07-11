#!/bin/sh
# Event-day one-command review: load credentials, force the verified provider,
# generate, then hard-gate on the scorecard (degraded / verdict / guard).
#
# Usage: bash scripts/event_review.sh <paper.md> <run-id>
set -eu

if [ $# -ne 2 ]; then
  echo "usage: bash scripts/event_review.sh <paper.md> <run-id>" >&2
  exit 2
fi

ENV_FILE=${ENV_FILE:-/Users/family/jason/Vtube/.env}
if [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi
export LLM_PROVIDER=${LLM_PROVIDER:-openai}

PY=python3
[ -x .venv/bin/python ] && PY=.venv/bin/python

"$PY" scripts/generate_see_through_review.py --paper "$1" --run-id "$2"

"$PY" - "$2" <<'EOF'
import json, sys

card = json.load(open(f"runs/{sys.argv[1]}/review_scorecard.json"))
problems = []
if card.get("degraded"):
    problems.append(f"degraded: {card.get('degraded_reason')}")
if card.get("verdict") != "PASS":
    problems.append(f"verdict={card.get('verdict')}")
if card.get("hallucination_guard_status") != "PASS":
    problems.append(f"hallucination_guard_status={card.get('hallucination_guard_status')}")
if problems:
    print("EVENT GATE FAIL: " + "; ".join(problems))
    sys.exit(1)
print(f"EVENT GATE PASS: mode={card['mode']} rec={card.get('overall_recommendation')}")
EOF
