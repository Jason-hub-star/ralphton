# Test Results

This file is the curated judge-facing summary. Full generated artifacts live in
`runs/`, and archived internal harness evidence lives in `runs/archive/`.

## Two-Layer Generator (2026-07-09)

The generator is now LLM brain + deterministic guards:

- Hardcoded off-scope filler removed; `filtered_criticisms` now comes from a
  real partition (LLM self-review flags + token-overlap threshold), so
  `off_scope_filtered_count` varies per paper.
- LLM path (`scripts/llm_client.py`, Anthropic default / `LLM_PROVIDER=openai`
  switch): 3 guarded stages — extraction, criticism drafting, self-review.
  Guards verify every quote verbatim against the paper and every evidence ref
  against extracted ids; one retry, then degrade to the heuristic path with
  `"degraded": true`.
- Review now follows the ICML form (Summary / Claims and Evidence / Relation
  to Prior Works / Other Aspects / Questions for Authors / Ethical Issues /
  Overall Recommendation 1–5) with rubric-anchored scores. The anchor mapping
  spans the full 1–5 range across claim-support profiles (verified: 3/3
  supported→5, 3/4→4, 2/3→3, 1/3→2, 0/3→1).
- Degrade path verified end to end: with no credentials,
  `runs/review-llm-001` completed as `mode=heuristic degraded=True` with the
  auth error recorded in `degraded_reason`.
- Regression after the rewrite: `eval-real-002`..`eval-real-006` all metrics
  1.0000 PASS; `eval-010`/`eval-011` identical to the `eval-009` baseline
  (layer_accuracy 1.0000, target_claim_accuracy 0.9333). `eval-011` archived.

## Live LLM-Path Verification (2026-07-09, provider=openai/gpt-5.1)

| run | mode | rec | claims | supported | kept | filtered | quotes verified | guard |
|---|---|---:|---:|---:|---:|---:|---|---|
| review-llm-case-001 | llm | 3 | 5 | 3 | 2 | 1 | 2/2 | PASS |
| review-llm-case-002 | llm | 4 | 4 | 3 | 2 | 1 | 2/2 | PASS |
| review-llm-case-003 | llm | 4 | 4 | 3 | 2 | 2 | 2/2 | PASS |
| review-llm-freeform | llm | 4 | 6 | 4 | 4 | 1 | 4/4 | PASS |

Read:

- All four papers completed the full 3-stage LLM pipeline with the
  hallucination guard PASS — every quoted span verified verbatim (after
  typographic normalization) against the paper.
- `off_scope_filtered_count` now varies per paper (1/1/2/1) — the filter is a
  real judgment, not a fixture.
- Scores differentiate (3 vs 4) and free-form ingestion extracts multiple
  claims (6) where the offline path degenerates to 1.
- The next-experiment selector prefers criticisms that target
  `needs_experiment` claims, so the proposed experiment lands on the claim
  the paper itself left unproven.
- Found and fixed during live runs: quote guard rejected typographic
  variants (curly quotes/dashes — normalization added), reasoning-token
  truncation on the OpenAI provider (token headroom + reasoning effort knob),
  double-numbered questions, and experiment selection on supported claims.

## Ralph Loop Harness (2026-07-09)

`PROMPT.md` (fresh-context iteration contract, deterministic gates as judge,
promise tags) + `TASKS.md` (event-day backlog) + `loop.sh` (runner-neutral,
max-iterations cap). Dry-run verified with stub runners: CONTINUE loops to the
cap and exits 1; COMPLETE exits 0 on detection.

## Track 2 Generated Review MVP

Commands:

```bash
python3 scripts/generate_see_through_review.py --paper examples/paper.md --run-id review-001
python3 scripts/generate_see_through_review.py --paper fixtures-unseen-3/case-001/paper.md --run-id review-002
```

Artifacts:

- `runs/review-001/generated_review.md`
- `runs/review-001/evidence_layers.json`
- `runs/review-001/review_scorecard.json`
- `runs/review-001/author_next_experiment.yaml`
- `runs/review-002/generated_review.md`
- `runs/review-002/evidence_layers.json`
- `runs/review-002/review_scorecard.json`
- `runs/review-002/author_next_experiment.yaml`

Scorecards:

| run | verdict | claim_count | supported_claims | needs_experiment_claims | generated_criticisms | off_scope_filtered | guard |
|---|---|---:|---:|---:|---:|---:|---|
| review-001 | PASS | 3 | 2 | 1 | 1 | 2 | PASS |
| review-002 | PASS | 3 | 2 | 1 | 1 | 2 | PASS |

Read:

- The generator produces all ICML-style review sections.
- The generator now classifies claim support before writing the review.
- Every emitted weakness links to a target claim and evidence source.
- Off-scope candidate criticisms are filtered before the review is emitted.
- The author gets one next experiment with a paper-specific metric and keep/discard condition.

Current limitation:

- This is deterministic and heuristic-based. It validates the artifact shape and loop mechanics, not final review intelligence.

## Internal Validation Harness

The old review-audit path is preserved as the regression harness. It checks whether review criticisms are grounded, mapped to the right claim, and converted into the right next experiment.

Latest archived command:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-009 --archive
python3 scripts/summarize_runs.py --output runs/run_summary.md
```

Latest harness metrics:

| metric | value |
|---|---:|
| cases | 5 |
| criticisms | 15 |
| layer_accuracy | 1.0000 |
| target_claim_accuracy | 0.9333 |
| off_scope_catch_rate | 1.0000 |
| grounded_preservation_rate | 1.0000 |
| next_experiment_precision | 1.0000 |
| raw_next_experiment_precision | 0.4000 |
| see_through_next_experiment_gain | 0.6000 |

Latest archive:

```text
runs/archive/20260709T165936_eval-009
```

## Track 1-Style Extraction Eval

Command:

```bash
python3 scripts/evaluate_real_review_agent.py --fixtures fixtures-real --run-id eval-real-001
```

Fixture note:

- `fixtures-real/` contains realistic local surrogate Track 1-style papers.
- A local workspace search did not find confirmed original Ralphthon Track 1 paper artifacts.
- Public web search found event descriptions, but no indexed original Track 1 paper artifacts.

Artifacts:

- `runs/eval-real-001/metrics.json`
- `runs/eval-real-001/case_table.md`
- `runs/eval-real-001/scorecard.log`
- `runs/eval-real-001/cases/*/generated_review.md`

Metrics:

| metric | value |
|---|---:|
| cases | 3 |
| claim_count_accuracy | 1.0000 |
| claim_status_accuracy | 1.0000 |
| evidence_ref_recall | 1.0000 |
| evidence_ref_precision | 1.0000 |
| limitation_recall | 1.0000 |
| selected_target_accuracy | 1.0000 |

Result:

```text
PASS
```

Confirmed paper intake:

- `docs/REAL-PAPER-INTAKE.md`
- `scripts/prepare_real_paper_intake.py`

Dry-run checked:

```bash
python3 scripts/prepare_real_paper_intake.py fixtures-real/case-001/paper.md fixtures-real/case-002/paper.md fixtures-real/case-003/paper.md --dry-run
```

Known miss:

- One weak small-sample criticism maps to a plausible but non-labeled target claim, so target-claim accuracy remains `0.9333`.

## Archive Integrity

Run summary:

- `runs/run_summary.md`
- `runs/index.jsonl`
- `runs/current/eval-009.txt`

Expected archive check:

```text
archive_integrity: PASS
```

## Decision

Review See-Through is now aligned with Ralphthon Track 2 as a Review Agent:

- paper in,
- ICML-style review out,
- evidence layers attached,
- off-scope requests filtered,
- one next Ralph Loop experiment emitted.

The next meaningful test is real Track 1 paper input plus constrained semantic extraction.
