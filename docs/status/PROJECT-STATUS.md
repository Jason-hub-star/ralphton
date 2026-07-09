# Project Status

## Current Truth

- Project: Review See-Through for Ralphthon Track 2.
- Current product direction: paper -> evidence-linked ICML-form review -> author next experiment.
- Generator is two-layer: LLM brain (extract -> criticize -> self-review, via `scripts/llm_client.py`) + deterministic guards (verbatim-quote check, evidence-ref check, off-scope partition, rubric-anchored 1-5 scoring). `--offline` forces the heuristic path; guard failure or missing credentials degrades to it with `"degraded": true`.
- Hardcoded off-scope filler is gone; `filtered_criticisms` is a real per-paper partition.
- Ralph loop harness: `PROMPT.md` + `TASKS.md` + `loop.sh` (runner-neutral, promise tags, deterministic gates as judge).
- Latest regression runs after the rewrite: `eval-real-002` (PASS, all 1.0000), `eval-010` (baseline preserved).
- Live LLM-path verification: pending API credentials.
- Track 1-style extraction eval: `eval-real-002`.
- Confirmed paper intake path: `docs/REAL-PAPER-INTAKE.md`.
- Latest archived harness run: `eval-009 @ 20260709T165936`.
- Current archive pointer: `runs/current/eval-009.txt`.
- Evidence ledger: `runs/index.jsonl`.
- Current run summary: `runs/run_summary.md`.
- Repo: https://github.com/Jason-hub-star/ralphton

## Current Metrics

Generated-review scorecards:

| run | verdict | claim_count | supported_claims | needs_experiment_claims | generated_criticisms | off_scope_filtered | guard |
|---|---|---:|---:|---:|---:|---:|---|
| review-001 | PASS | 3 | 2 | 1 | 1 | 2 | PASS |
| review-002 | PASS | 3 | 2 | 1 | 1 | 2 | PASS |

Internal harness, from the latest `fixtures-unseen-3` archived run:

| metric | value |
|---|---:|
| layer_accuracy | 1.0000 |
| target_claim_accuracy | 0.9333 |
| off_scope_catch_rate | 1.0000 |
| grounded_preservation_rate | 1.0000 |
| next_experiment_precision | 1.0000 |
| raw_next_experiment_precision | 0.4000 |
| see_through_next_experiment_gain | 0.6000 |

Track 1-style extraction eval, from `runs/eval-real-001/metrics.json`:

| metric | value |
|---|---:|
| claim_count_accuracy | 1.0000 |
| claim_status_accuracy | 1.0000 |
| evidence_ref_recall | 1.0000 |
| evidence_ref_precision | 1.0000 |
| limitation_recall | 1.0000 |
| selected_target_accuracy | 1.0000 |

## What Works

- The Track 2 script now generates ICML-style review sections directly from a paper.
- Claims are classified as `supported`, `needs_experiment`, or `weak` before review emission.
- Each generated weakness is linked to claim/evidence layers.
- The selected author experiment now carries a paper-specific metric and keep/discard condition.
- `fixtures-real/` now tests claim/evidence/limitation extraction on three Track 1-style papers.
- `scripts/prepare_real_paper_intake.py` can stage confirmed paper files into `fixtures-real-pending/` with draft labels for human review.
- Off-scope candidate criticisms are filtered before review emission.
- The author-facing output includes one next experiment.
- The older review-audit evaluator still checks layer accuracy, target-claim mapping, off-scope filtering, and next-experiment selection.
- `--archive` preserves immutable harness evidence under `runs/archive/`.

## Known Weaknesses

- The LLM path has not run live yet (no API credentials in the dev environment); only the degrade path is verified end to end.
- The offline heuristic path still degenerates on free-form papers (abstract becomes a single claim); free-form ingestion is an LLM-path feature.
- `fixtures-real/` are local surrogate papers, not confirmed original Ralphthon Track 1 submissions, and all three share the same claim profile (2/3 supported), so they cannot demonstrate score differentiation by themselves.
- Internal harness `target_claim_accuracy` remains `0.9333`, mostly from lexical claim matching.
- The OpenAI provider branch in `scripts/llm_client.py` is untested; its default model name must be confirmed at the event.
- Mutable `runs/<run-id>/` remains useful for latest local inspection, while archived eval runs are the evidence source of record.

## Next Loop

- Run the LLM path live on `fixtures-real/` and `examples/freeform-paper.md` once credentials are available; archive the results.
- Replace surrogate `fixtures-real/` papers with confirmed event papers when available (`docs/REAL-PAPER-INTAKE.md`).
- Add line references alongside verbatim quotes in evidence layers.
- Keep `eval-* --archive` as the regression gate after generator changes.

## Record Locations

- Generated reviews: `runs/review-001/`, `runs/review-002/`.
- Curated summary: `docs/TEST-RESULTS.md`.
- Detailed daily logs: `docs/daily/2026-07-09-append-only-run-archive.md`, `docs/daily/2026-07-09-track2-review-agent-realignment.md`.
- Immutable archive: `runs/archive/`.
- Latest pointer files: `runs/current/`.
- Ledger: `runs/index.jsonl`.
- Summary: `runs/run_summary.md`.
- Real extraction eval: `runs/eval-real-001/`.
- Confirmed paper intake: `docs/REAL-PAPER-INTAKE.md`.
