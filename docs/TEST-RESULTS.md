# Test Results

This file is the curated judge-facing summary. Full generated artifacts live in
`runs/`, and archived internal harness evidence lives in `runs/archive/`.

## Event-Day Rehearsal + Runner Chain (2026-07-11)

Full unattended rehearsal of the event flow on branch `rehearsal-dry-run`:
paper intake -> gated wrapper review (`scripts/event_review.sh`) -> audit
archive -> weakest-metric improvement -> docs refresh, driven end to end by a
sandboxed Codex runner. Result: `[loop] COMPLETE after 6 iteration(s)`;
`review-event-001` scorecard mode=llm, degraded=False, guard PASS.

Found and fixed by the rehearsal:

- `loop.sh` false COMPLETE: `codex exec` echoes PROMPT.md into stdout, so the
  unanchored tag grep matched the prompt's own tag documentation at iteration
  1. Tags now match only on bare `^<promise>` lines.
- Codex's sandbox blocks `.git` writes; the runner line now passes
  `sandbox_workspace_write.writable_roots=["$PWD/.git"]` so loop commits work
  without dropping the sandbox.
- PROMPT.md contradiction: "improve the weakest metric" was impossible while
  `review_see_through.py` sat on the never-edit judge list. It is now declared
  system-under-test (judges: `evaluate_*.py` + labels), and the offline
  baseline tightened to include `target_claim_accuracy=1.0000`.
- The rehearsal loop's own 1-line classifier improvement (weak criticisms now
  target the lexically matched claim) was adopted on main:
  `target_claim_accuracy` 0.9333 -> 1.0000, all other metrics at baseline.

Final pre-event verification (2026-07-11 evening): all five chain runners
live-verified (Codex gmdqn2tp — two full rehearsals; Codex umjitak — exec OK
after login; `claude -p --dangerously-skip-permissions` — full tool cycle of
file write + git commit + bare tag inside the loop; Sonnet flag combo; Codex
on API-key billing — exec OK). Edge papers through the gated wrapper: a
Korean free-form paper (6 claims, 2/2 quotes verbatim-verified, real
off-scope partition, GATE PASS) and a 208K-char synthetic paper (mode=llm,
GATE PASS, no truncation). Three-paper intake staged cleanly; archive
integrity PASS.

Same-day hardening for unattended runs: intake preflight (clean error on an
unmatched glob), loop fail-fast on a missing promise tag, Hangul token support
in the off-scope filter, `scripts/event_review.sh` (loads credentials, forces
`LLM_PROVIDER=openai`, hard-gates degraded/verdict/guard), and the
`runners.conf` fallback chain (two Codex subscriptions -> Claude -> Sonnet ->
Codex on metered API billing) with rotation and backoff in `loop.sh`.

### Track 1 Harness Rehearsal

Gate scorecards:

```text
[2026-07-11 21:27:44] run=track1-gate-001 paper=track1/paper.md sections=OK claims=5 needs_experiment=1 evidence_rows=10 verified=10/10 limitations=3 verdict=PASS
[2026-07-11 21:31:24] run=track1-gate-002 paper=track1/paper.md sections=OK claims=6 needs_experiment=1 evidence_rows=12 verified=12/12 limitations=3 verdict=PASS
[2026-07-11 21:32:45] run=track1-gate-002 paper=track1/paper.md sections=OK claims=6 needs_experiment=1 evidence_rows=12 verified=12/12 limitations=3 verdict=PASS
[2026-07-11 21:38:18] run=track1-gate-002 paper=track1/paper.md sections=OK claims=6 needs_experiment=1 evidence_rows=12 verified=12/12 limitations=3 verdict=PASS
[2026-07-11 21:38:25] run=track1-gate-002 paper=track1/paper.md sections=OK claims=6 needs_experiment=1 evidence_rows=12 verified=12/12 limitations=3 verdict=PASS
```

Self-review recommendations:

| run | mode | degraded | verdict | overall_recommendation |
|---|---|---|---|---:|
| track1-review-001 | llm | false | PASS | 3 |
| track1-review-002 | llm | false | PASS | 4 |

Found and fixed by this rehearsal: the scorecard verdict conflated "all draft
criticisms judged off-scope" with "pipeline produced nothing". The honest
revision after `track1-review-001` left no grounded weakness — all three
drafts were filtered — and the review failed its own verdict despite guard
PASS and recommendation 4. `generate_see_through_review.py` now passes a
review whose drafts were all legitimately filtered and fails only when
nothing was drafted; both Track 2 regression gates re-verified at baseline
after the fix. The closed loop (paper gate → self-review → revision →
next-experiment seed in `track1/NEXT.md`) completed end to end, and every
number in `track1/paper.md` is verified against archived ground truth
(12/12 evidence rows).

## Loop Engine Guards (2026-07-12)

Post-rehearsal hardening of `loop.sh` — three deterministic guards that run
outside the model:

- Protected-path check: any change to the judges, loop contracts, `loop.sh`,
  `start.sh`, `runners.conf`, fixture labels, `runs/archive/`, or
  `runs/index.jsonl` between iteration start and the promise tag stops the
  loop. The never-edit rules are now enforced by the engine, not only
  promised in the prompt contract.
- Runner timeout: a runner still running after `RALPH_RUNNER_TIMEOUT`
  seconds (default 3600) is killed with its whole process group and then
  handled by the existing tagless-rotation path — no new failure state.
- Stall stop: `RALPH_STALL_MAX` (default 2) consecutive CONTINUE iterations
  without a new commit stop the loop instead of burning the chain.

Stub-runner guard rig, 12/12 PASS: committed and uncommitted judge edits
both stopped the loop; a legitimate 3-commit run completed with no false
positive; simple and compound hung runners were killed in ~5s with no orphan
output (process-group kill); the stall guard stopped at iteration 2;
rotation, BLOCKED handling, and `RALPH_PROMPT` contract switching are
unchanged. Real-repo smoke after merge: stub COMPLETE run exits 0.

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
