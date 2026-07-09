# Loop Backlog — Ralphthon Event Day

One task per loop iteration, top-down. Mark `[x]` only after the gates in
`PROMPT.md` pass. Replace the placeholder paper names when the Track 1 papers
arrive.

- [ ] Intake: copy each received Track 1 paper into `papers/incoming/`, then
  stage draft labels with
  `python3 scripts/prepare_real_paper_intake.py papers/incoming/*.md --output fixtures-real-pending`
- [ ] Generate a review for the first incoming paper:
  `python3 scripts/generate_see_through_review.py --paper papers/incoming/<paper>.md --run-id review-event-001`
  (gate: verdict PASS, hallucination guard PASS, not degraded)
- [ ] Generate reviews for the remaining incoming papers
  (`review-event-002`, `review-event-003`, ...)
- [ ] Self-verify: run the internal audit harness against the generated
  reviews and archive the evidence
  (`python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id loop-regress --archive`)
- [ ] Improve the single weakest metric surfaced by the archived run
  (one metric only; re-run the archive gate after)
- [ ] Final: refresh `docs/TEST-RESULTS.md` with the latest scorecards and
  commit
