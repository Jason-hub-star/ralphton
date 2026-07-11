#!/bin/sh
# Runner-neutral Ralph loop: every iteration re-reads PROMPT.md with fresh
# context, does exactly one task from TASKS.md, is judged by the
# deterministic gate scripts, commits on pass, and reports via a
# <promise>CONTINUE|COMPLETE|BLOCKED</promise> tag that the loop parses.
#
# Runner selection (first match wins):
#   RALPH_RUNNER="claude -p" bash loop.sh          # single runner override
#   runners.conf (or RALPH_RUNNERS_FILE)           # fallback chain, one command per line
#   default: claude -p
#
# Contract selection:
#   RALPH_PROMPT=track1/PROMPT.md bash loop.sh     # alternate loop contract (default PROMPT.md)
#
# Codex runner line (network on for the LLM call, .git writable for commits):
#   codex exec --sandbox workspace-write \
#     -c sandbox_workspace_write.network_access=true \
#     -c 'sandbox_workspace_write.writable_roots=["'"$PWD"'/.git"]' -
#
# Chain semantics (multi-hour, unattended):
#   - A runner that emits no bare <promise> tag (crash, usage limit) is
#     rotated out for the same task; tracked files are reset first
#     (git checkout -- .) so the next runner starts clean. Do not start the
#     loop with uncommitted work you care about.
#   - <promise>BLOCKED> stops the loop: a task problem survives runner swaps.
#   - When the whole chain fails, wait RALPH_RETRY_WAIT seconds (default 900)
#     and retry, up to RALPH_RETRY_MAX (default 3) attempts per iteration —
#     subscription windows reopen over time.
#
# The loop is fresh-context by design: PROMPT.md is re-read from disk every
# iteration, and the only carried state is the repository itself.
set -u

MAX_ITER=20
RETRY_MAX=${RALPH_RETRY_MAX:-3}
RETRY_WAIT=${RALPH_RETRY_WAIT:-900}
PROMPT_FILE=${RALPH_PROMPT:-PROMPT.md}
if [ ! -f "$PROMPT_FILE" ]; then
  echo "prompt file not found: $PROMPT_FILE" >&2
  exit 2
fi
while [ $# -gt 0 ]; do
  case "$1" in
    --max-iterations) MAX_ITER="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

LOG_DIR="runs/loop/$(date +%Y%m%dT%H%M%S)-$$"
mkdir -p "$LOG_DIR"

RUNNERS_FILE=${RALPH_RUNNERS_FILE:-runners.conf}
ACTIVE="$LOG_DIR/runners.active"
if [ -n "${RALPH_RUNNER:-}" ]; then
  printf '%s\n' "$RALPH_RUNNER" > "$ACTIVE"
elif [ -f "$RUNNERS_FILE" ]; then
  grep -v -e '^[[:space:]]*#' -e '^[[:space:]]*$' "$RUNNERS_FILE" > "$ACTIVE"
else
  printf 'claude -p\n' > "$ACTIVE"
fi
echo "[loop] contract: $PROMPT_FILE"
echo "[loop] runner chain ($(grep -c '' "$ACTIVE")):"
sed 's/^/[loop]   /' "$ACTIVE"

for i in $(seq 1 "$MAX_ITER"); do
  attempt=1
  TAG_LOG=""
  while [ -z "$TAG_LOG" ]; do
    r=0
    while IFS= read -r RUNNER; do
      r=$((r+1))
      LOG="$LOG_DIR/iter-$i-a$attempt-r$r.log"
      echo "[loop] iteration $i/$MAX_ITER attempt $attempt runner $r: $RUNNER"
      sh -c "$RUNNER" < "$PROMPT_FILE" 2>&1 | tee "$LOG"
      # Anchored to line start: runners like `codex exec` echo PROMPT.md
      # (which quotes the tags, indented) back into stdout; only a bare tag
      # line counts.
      if grep -q "^<promise>" "$LOG"; then
        TAG_LOG="$LOG"
        break
      fi
      echo "[loop] no promise tag from runner $r — resetting tracked files, rotating"
      git checkout -- .
    done < "$ACTIVE"
    [ -n "$TAG_LOG" ] && break
    if [ "$attempt" -ge "$RETRY_MAX" ]; then
      echo "[loop] chain failed $RETRY_MAX time(s) at iteration $i — giving up. Logs: $LOG_DIR"
      exit 1
    fi
    attempt=$((attempt + 1))
    echo "[loop] chain exhausted — waiting ${RETRY_WAIT}s for usage windows (attempt $attempt/$RETRY_MAX)"
    sleep "$RETRY_WAIT"
  done
  if grep -q "^<promise>COMPLETE</promise>" "$TAG_LOG"; then
    echo "[loop] COMPLETE after $i iteration(s). Logs: $LOG_DIR"
    exit 0
  fi
  if grep -q "^<promise>BLOCKED" "$TAG_LOG"; then
    echo "[loop] BLOCKED at iteration $i — see $TAG_LOG"
    exit 1
  fi
done

echo "[loop] hit max iterations ($MAX_ITER) without COMPLETE. Logs: $LOG_DIR"
exit 1
