# Test Results

This file is the curated judge-facing summary. Full generated artifacts live in
`runs/`, and archived internal harness evidence lives in `runs/archive/`.

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
