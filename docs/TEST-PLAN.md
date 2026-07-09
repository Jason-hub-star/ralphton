# Review See-Through Test Plan

## Test Goal

Check whether Review See-Through makes a generated Track 2 review more useful for Ralph Loop.

Useful means:

- the review is emitted in ICML-style sections,
- unsupported criticism becomes visible,
- grounded criticism is preserved,
- weak criticism becomes a concrete missing-evidence item,
- the next iteration gets one small experiment instead of broad advice.

## Hypothesis

If a Review Agent generates an ICML-style review with transparent evidence layers, then the next Ralph Loop iteration will be easier to execute because the system can choose one measurable experiment.

## Baseline

Baseline review workflow:

1. read review,
2. accept criticism at face value,
3. ask author agent to revise.

Problem:

- review may contain hallucinated or off-scope criticism,
- weak criticism may be directionally right but not actionable,
- author agent may revise prose instead of running evidence.

## Treatment

Review See-Through workflow:

1. read paper,
2. extract claims and evidence,
3. generate ICML-style review sections,
4. link weaknesses to evidence layers,
5. filter off-scope candidate criticisms,
6. choose one author-facing next experiment,
7. write scorecard.

Internal harness workflow:

1. read paper and review,
2. map criticism to paper claims,
3. classify criticism into layers,
4. extract hidden assumptions,
5. choose one next experiment,
6. write scorecard.

## Fixture

Use:

- `examples/paper.md`
- `fixtures-unseen-3/case-001/paper.md`
- `fixtures-real/` for Track 1-style generated-review extraction
- `examples/review.md` for the internal audit harness only

The generator fixtures intentionally contain:

- concrete paper claims,
- explicit evidence,
- at least one missing experiment or limitation.

## Pass Criteria

The generated-review MVP passes if:

- `generated_review.md` contains Summary, Strengths, Weaknesses, Questions for Authors, Soundness, Presentation, Contribution, Rating, and Confidence,
- `evidence_layers.json` contains claims, evidence, limitations, generated criticisms, filtered criticisms, and selected next experiment,
- `review_scorecard.json` reports `hallucination_guard_status=PASS`,
- `author_next_experiment.yaml` selects exactly one experiment.

The internal harness passes if:

- `review_layers.json` contains 3 criticisms,
- one criticism is `grounded`,
- one criticism is `weak`,
- one criticism is `off_scope`,
- `experiment_card.yaml` selects exactly one experiment,
- `scorecard.log` has an append-only verdict line.

## Effectiveness Metrics

### Transparency Precision

How many review criticisms receive a non-vague layer label?

Target for fixture: `3/3`.

### Hallucination / Off-Scope Catch

Does the system flag review text that is not grounded in the paper?

Target for fixture: yes.

### Next-Experiment Sharpness

Does the output choose one bounded experiment with:

- hypothesis,
- baseline,
- metric,
- keep condition,
- discard condition?

Target for fixture: yes.

### Ralph Loop Readiness

Can the scorecard line be used as the next iteration input without rereading the whole paper?

Target for fixture: yes.

## Manual Review Questions

After running the script, ask:

1. Would a human author know what to do next?
2. Did the tool suppress at least one bad review instruction?
3. Did it preserve the useful criticism?
4. Did it avoid broad "do more experiments" advice?

## Next Test After Fixture

Replace `fixtures-real/` with confirmed original Track 1 event papers when they become available. The next test should add constrained semantic extraction but keep the same output schema.
