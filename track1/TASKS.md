# Track 1 Backlog — Paper-Writing Loop

Topic: "Review See-Through: decomposing paper reviews into transparent
evidence layers" — a paper about THIS repository's review agent, citing only
measured results. Ground-truth files to cite (verify keys by opening them):

- `runs/archive/20260711T212137_eval-012/metrics.json` — harness metrics:
  layer_accuracy, target_claim_accuracy, off_scope_catch_rate,
  next_experiment_precision, raw_next_experiment_precision,
  see_through_next_experiment_gain, case_count, criticism_count
- `runs/eval-real-001/metrics.json` — extraction eval: claim_count_accuracy,
  claim_status_accuracy, evidence_ref_recall, evidence_ref_precision,
  limitation_recall, selected_target_accuracy

To reuse this harness for a new topic: replace this Topic block and the tasks
below; the contract (`track1/PROMPT.md`) and the judges stay unchanged. If the
new topic needs fresh measurements, add a first task that produces
`runs/<exp-id>/metrics.json` (outside `runs/track1*`) and cite those keys.

One task per loop iteration, top-down. Mark `[x]` only after the gates in
`track1/PROMPT.md` pass.

- [x] Draft `track1/paper.md` per the paper spec in `track1/PROMPT.md`
  (5 required sections; evidence table with `path#key` sources; at least one
  `(needs experiment)` claim). Gate:
  `python3 scripts/evaluate_track1_paper.py track1/paper.md --run-id track1-gate-001`
- [x] Self-review the paper with the Track 2 review agent:
  `bash scripts/track1_selfreview.sh track1/paper.md track1-review-001 3`
- [x] Revise: read `runs/track1-review-001/generated_review.md`, address the
  single most important weakness in `track1/paper.md`, then re-pass BOTH
  gates: `python3 scripts/evaluate_track1_paper.py track1/paper.md --run-id track1-gate-002`
  and `bash scripts/track1_selfreview.sh track1/paper.md track1-review-002 <rec>`
  where `<rec>` is the overall_recommendation from
  `runs/track1-review-001/review_scorecard.json` (the revision must not score
  lower).
- [x] Closed loop: summarize `runs/track1-review-002/author_next_experiment.yaml`
  into `track1/NEXT.md` — what to run in the next loop cycle, the expected
  metric, and the keep/discard condition. No gate script for this task: the
  file must exist, be non-empty, and name the metric.
- [ ] Final: add a "Track 1 Harness Rehearsal" subsection to
  `docs/TEST-RESULTS.md` quoting the gate scorecard lines
  (`runs/track1-gate-00*/track1_gate.log`) and both self-review
  recommendations, then commit.
