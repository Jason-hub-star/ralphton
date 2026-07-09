# Ralph Loop Prompt — Review See-Through (Ralphthon Track 2)

You are ONE iteration of an autonomous loop. Your context is fresh: everything
you need is in this file, `TASKS.md`, and the repository. Do not assume any
memory of previous iterations — state lives only in files and git history.

## Iteration contract (follow exactly)

1. Read `TASKS.md`. Pick the FIRST unchecked task (`- [ ]`). Do ONLY that task.
2. Make the smallest change that can pass the gates.
3. Run the gates. The deterministic scripts are the judge — never declare PASS
   yourself. Use `.venv/bin/python` if it exists, otherwise `python3`.
   - Offline regression (must stay at baseline: every case PASS,
     `layer_accuracy=1.0000`):
     `python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id loop-regress`
   - Extraction regression (must print `verdict=PASS`):
     `python3 scripts/evaluate_real_review_agent.py --fixtures fixtures-real --run-id loop-real`
   - If the task generated a review: its `runs/<id>/review_scorecard.json`
     must show `"verdict": "PASS"` and `"hallucination_guard_status": "PASS"`.
4. If all gates pass: mark the task `[x]` in `TASKS.md`, then
   `git add -A && git commit -m "loop: <task summary>"`.
   If the task was a review milestone, also archive evidence:
   `python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id loop-regress --archive`
5. If a gate fails: fix and retry ONCE. If it fails again, revert your change
   (`git checkout -- .`) and report BLOCKED.
6. End your output with exactly one promise tag on its own final line:
   - `<promise>CONTINUE</promise>` — this task is done, unchecked tasks remain
   - `<promise>COMPLETE</promise>` — every task in TASKS.md is checked
   - `<promise>BLOCKED: <one-line reason></promise>` — cannot proceed

## Guardrails

- One task per iteration. Do not edit, reorder, or add tasks except marking
  your own task `[x]`.
- Never edit the judges: `scripts/evaluate_*.py`, `scripts/review_see_through.py`,
  `fixtures*/labels.json`. Passing gates by weakening them is failure.
- Never delete or rewrite `runs/archive/`, `runs/index.jsonl`, or git history.
- LLM path: `generate_see_through_review.py` calls the LLM by default and
  needs `ANTHROPIC_API_KEY` (or `LLM_PROVIDER=openai` + `OPENAI_API_KEY`).
  If credentials are missing the script degrades to the offline heuristic and
  records `"degraded": true` — treat a degraded review of a real paper as a
  gate failure and report BLOCKED instead of committing it.

## Project spec (re-read every iteration — do not drift from this)

Review See-Through is a Track 2 Review Agent: a Track 1-style paper goes in,
an ICML-form review comes out (Summary / Claims and Evidence / Relation to
Prior Works / Other Aspects / Questions for Authors / Ethical Issues /
Overall Recommendation 1–5). Every weakness is linked to a claim id and
evidence layer, quotes are verified verbatim against the paper, off-scope
criticisms are filtered before emission, and the review ends with exactly one
bounded next experiment for the authors. Artifacts per run:
`generated_review.md`, `evidence_layers.json`, `review_scorecard.json`,
`author_next_experiment.yaml` under `runs/<run-id>/`.
