# 2026-07-09 Track 2 Review Agent Realignment

## Change

Repositioned Review See-Through from "audit an AI-generated review" to "generate an evidence-linked ICML-style review from a paper."

## Why

Ralphthon Track 2 asks for a Review Agent that reviews papers from Track 1. Auditing a review is still useful, but it is not the main product surface.

## Implementation

- Added `scripts/generate_see_through_review.py`.
- Kept `scripts/review_see_through.py` and `scripts/evaluate_review_see_through.py` as the internal validation harness.
- Generated review outputs:
  - `generated_review.md`
  - `evidence_layers.json`
  - `review_scorecard.json`
  - `author_next_experiment.yaml`
- Updated README, spec, test plan, test results, and project status around the Track 2 direction.

## Evidence

Commands:

```bash
python3 scripts/generate_see_through_review.py --paper examples/paper.md --run-id review-001
python3 scripts/generate_see_through_review.py --paper fixtures-unseen-3/case-001/paper.md --run-id review-002
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-009 --archive
python3 scripts/summarize_runs.py --output runs/run_summary.md
python3 -m py_compile scripts/generate_see_through_review.py scripts/review_see_through.py scripts/evaluate_review_see_through.py scripts/summarize_runs.py
```

## Known Limits

- The generator is deterministic and template-based.
- It validates schema, evidence linkage, off-scope filtering, and next-experiment shape.
- It does not yet perform semantic novelty or methodology review.

## Next

Add constrained semantic extraction while preserving the same output files and regression harness.

## Review Agent Hardening Pass

Prompt:

```text
Track 2 제출용으로 generate_see_through_review.py를 실제 Review Agent답게 고도화해줘. 단, 출력 schema는 유지하고 eval-009 archive 하네스로 회귀검증까지 해줘.
```

Changes:

- Added claim support classification before review generation.
- Kept required output schema and file names unchanged.
- Added evidence-linked claim statuses: `supported`, `needs_experiment`, `weak`.
- Reduced duplicate/overbroad limitation criticism generation.
- Made the author next experiment more paper-specific with metric, baseline, keep condition, discard condition, and artifact request.
- Kept old audit/eval scripts unchanged as the regression harness.

Evidence:

```bash
python3 scripts/generate_see_through_review.py --paper examples/paper.md --run-id review-001
python3 scripts/generate_see_through_review.py --paper fixtures-unseen-3/case-001/paper.md --run-id review-002
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-009 --archive
python3 scripts/summarize_runs.py --output runs/run_summary.md
python3 -m py_compile scripts/generate_see_through_review.py scripts/review_see_through.py scripts/evaluate_review_see_through.py scripts/summarize_runs.py
```

Latest archive:

```text
runs/archive/20260709T165420_eval-009
```

Result:

- `review-001`: PASS, 2 supported claims, 1 needs-experiment claim, 1 generated criticism.
- `review-002`: PASS, 2 supported claims, 1 needs-experiment claim, 1 generated criticism.
- Internal harness: layer accuracy `1.0000`, target claim accuracy `0.9333`, next experiment precision `1.0000`.

## Track 1-Style Fixture Eval

Prompt:

```text
실제 Track 1 논문 3개를 fixtures-real/에 넣고, generate_see_through_review.py가 각 논문에서 claim/evidence/limitation을 얼마나 잘 뽑는지 별도 evaluator까지 만들어줘. 기존 eval-009 archive regression은 유지해줘.
```

Reality check:

- No confirmed original Ralphthon Track 1 paper artifacts were found in the local workspace search.
- Created `fixtures-real/` as realistic local surrogate Track 1-style papers with frozen gold labels.

Added:

- `fixtures-real/case-001/`
- `fixtures-real/case-002/`
- `fixtures-real/case-003/`
- `scripts/evaluate_real_review_agent.py`

Evidence:

```bash
python3 scripts/evaluate_real_review_agent.py --fixtures fixtures-real --run-id eval-real-001
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-009 --archive
python3 scripts/summarize_runs.py --output runs/run_summary.md
python3 -m py_compile scripts/generate_see_through_review.py scripts/evaluate_real_review_agent.py scripts/review_see_through.py scripts/evaluate_review_see_through.py scripts/summarize_runs.py
```

Results:

- `eval-real-001`: PASS.
- `claim_count_accuracy`: `1.0000`.
- `claim_status_accuracy`: `1.0000`.
- `evidence_ref_recall`: `1.0000`.
- `evidence_ref_precision`: `1.0000`.
- `limitation_recall`: `1.0000`.
- `selected_target_accuracy`: `1.0000`.
- Latest regression archive: `runs/archive/20260709T165936_eval-009`.

## Confirmed Paper Intake Prep

Added a safe intake path for confirmed original Track 1 papers:

- `scripts/prepare_real_paper_intake.py`
- `docs/REAL-PAPER-INTAKE.md`

The script writes `labels.draft.json`, not `labels.json`, so generator predictions cannot accidentally become gold labels without human review.

Dry-run evidence:

```bash
python3 scripts/prepare_real_paper_intake.py fixtures-real/case-001/paper.md fixtures-real/case-002/paper.md fixtures-real/case-003/paper.md --dry-run
python3 -m py_compile scripts/prepare_real_paper_intake.py scripts/evaluate_real_review_agent.py scripts/generate_see_through_review.py
```
