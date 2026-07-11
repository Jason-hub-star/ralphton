#!/usr/bin/env bash
# Ralph loop runner (runner-neutral).
#
# Usage:
#   bash loop.sh [--max-iterations N]
#
# RALPH_RUNNER is any command that reads one prompt on stdin and runs a single
# agent iteration to completion, e.g.:
#   RALPH_RUNNER="claude -p"                      # Claude Code headless
#   RALPH_RUNNER="codex exec --full-auto -"       # Codex CLI (- = stdin)
#
# The loop is fresh-context by design: PROMPT.md is re-read from disk every
# iteration, and the only carried state is the repository itself.
set -u

MAX_ITER=20
while [ $# -gt 0 ]; do
  case "$1" in
    --max-iterations) MAX_ITER="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

RUNNER=${RALPH_RUNNER:-"claude -p"}
LOG_DIR="runs/loop/$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$LOG_DIR"

for i in $(seq 1 "$MAX_ITER"); do
  echo "[loop] iteration $i/$MAX_ITER (runner: $RUNNER)"
  LOG="$LOG_DIR/iter-$i.log"
  sh -c "$RUNNER" < PROMPT.md 2>&1 | tee "$LOG"
  if grep -q "<promise>COMPLETE</promise>" "$LOG"; then
    echo "[loop] COMPLETE after $i iteration(s). Logs: $LOG_DIR"
    exit 0
  fi
  if grep -q "<promise>BLOCKED" "$LOG"; then
    echo "[loop] BLOCKED at iteration $i — see $LOG"
    exit 1
  fi
  if ! grep -q "<promise>" "$LOG"; then
    echo "[loop] no promise tag at iteration $i — runner failed or crashed. See $LOG"
    exit 1
  fi
done

echo "[loop] max iterations ($MAX_ITER) reached without COMPLETE. Logs: $LOG_DIR"
exit 1
