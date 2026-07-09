# 2026-07-09 - append-only run archive

## Scope

- Work unit: Review See-Through run archive
- Change class: evaluation pipeline / docs ops
- Status update mode: thin-status + evidence-only

## Implementation

- Added `--archive` to `scripts/evaluate_review_see_through.py`.
- Kept the existing mutable `runs/<run-id>/` behavior unchanged.
- Archive mode copies report files to `runs/archive/<timestamp>_<run-id>/`.
- Archive mode writes `run_manifest.json` beside the copied reports.
- Archive mode updates `runs/current/<run-id>.txt` with the latest archive path.
- Archive mode appends one JSON row to `runs/index.jsonl`.

## Verification

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-008 --archive
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-008 --archive
python3 -m py_compile scripts/evaluate_review_see_through.py scripts/review_see_through.py
```

## Result

- First archive: `runs/archive/20260709T155757_eval-008/`
- Second archive: `runs/archive/20260709T155802_eval-008/`
- Latest pointer: `runs/current/eval-008.txt`
- Ledger: `runs/index.jsonl`
- Both archive directories preserved their own report files.

## Notes

- Existing `runs/<run-id>/` remains mutable for quick local inspection.
- Archive directories are the evidence source of record.
- `runs/current/<run-id>.txt` is intentionally mutable.

## Next Action

- Add a small archive integrity checker if run volume grows.
- Consider moving long historical eval notes from `docs/TEST-RESULTS.md` into daily or weekly rollups.

## Follow-up: Run Summary Tool

Implementation:

- Added `scripts/summarize_runs.py`.
- Reads `runs/index.jsonl`.
- Reports latest run, best run, recent metric deltas, aggregated error summary, and archive integrity.
- Checks archive report files, `run_manifest.json`, and `runs/current/<run-id>.txt` pointers.

Verification:

```bash
python3 scripts/summarize_runs.py
python3 scripts/summarize_runs.py --output runs/run_summary.md
python3 -m py_compile scripts/summarize_runs.py scripts/evaluate_review_see_through.py scripts/review_see_through.py
```

Result:

- Archive integrity: PASS.
- Best archived run: `eval-008 @ 20260709T155802`.
- Current next action: improve target-claim mapping or add constrained extraction.
- Summary snapshot: `runs/run_summary.md`.
