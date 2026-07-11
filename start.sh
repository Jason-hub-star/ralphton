#!/bin/sh
# Event-day launcher: one command per track, with preflight checks.
#
#   bash start.sh track2 [max-iterations=20]   # review incoming papers (default contract)
#   bash start.sh track1 [max-iterations=8]    # write the paper (track1/ contract)
#
# caffeinate keeps macOS awake for the whole run.
set -eu

case "${1:-}" in
  track2)
    if ! ls papers/incoming/*.md >/dev/null 2>&1; then
      echo "papers/incoming/ has no .md papers — save the received Track 1 papers there first." >&2
      exit 2
    fi
    exec caffeinate -is bash loop.sh --max-iterations "${2:-20}"
    ;;
  track1)
    if ! grep -q '^- \[ \]' track1/TASKS.md; then
      echo "track1/TASKS.md has no unchecked tasks — replace the Topic block and reset the" >&2
      echo "backlog with fresh run-ids (e.g. track1-event-*) so rehearsal artifacts survive." >&2
      exit 2
    fi
    RALPH_PROMPT=track1/PROMPT.md exec caffeinate -is bash loop.sh --max-iterations "${2:-8}"
    ;;
  *)
    echo "usage: bash start.sh track1|track2 [max-iterations]" >&2
    exit 2
    ;;
esac
