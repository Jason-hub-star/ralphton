# Review See-Through

Turning paper reviews into transparent evidence layers.

Review See-Through is a Ralphthon Track 2 idea. It does not try to replace a peer reviewer. It generates an ICML-style review and decomposes the review into visible layers:

- grounded criticism,
- weak criticism,
- unsupported or off-scope criticism,
- hidden assumptions,
- missing evidence,
- the smallest next Ralph Loop experiment.

For Track 2, the public-facing artifact is now a Review Agent:

- input is a Track 1-style paper,
- output is an ICML-style review,
- every weakness is linked to claim/evidence layers,
- off-scope criticisms are filtered before they reach the review,
- the review ends with one author-facing next experiment.

The older audit path is still useful, but it is now the internal validation harness for checking whether the generated review stays grounded.

The core bet:

> Review Agents become more useful when every criticism is separated into transparent evidence layers and converted into one runnable next experiment.

## Why This Angle

Many systems already review papers or check reproducibility. Review See-Through is narrower:

- input is the submitted paper,
- output is an ICML-style review plus transparent evidence layers,
- final action is one bounded experiment for the next Ralph Loop iteration.

This avoids competing with broad Auto Research operating systems. It focuses on the event mechanic: reviews should feed the next loop.

## Inspiration

`shitagaki-lab/see-through` decomposes a single anime image into semantic layers, depth, masks, and inferred hidden regions. Review See-Through applies that pattern to reviews:

- a review is the visible image,
- claims and evidence are semantic layers,
- hidden assumptions are occluded regions,
- missing experiments are inpaint targets,
- the next Ralph Loop experiment is the reconstruction step.

Local precedents:

- `jason-agent-harness-template/harnesses/autoresearch-loop.md`
- `jason-agent-harness-template/harnesses/evidence-review.md`
- `jason-agent-harness-template/harnesses/tiered-review.md`
- `Vtube/review_app/review_manifest.json`
- `unityctl workflow verify`

## MVP

Inputs:

- `examples/paper.md`
- optional audit fixture review: `examples/review.md`

Outputs:

- `runs/<id>/generated_review.md`
- `runs/<id>/evidence_layers.json`
- `runs/<id>/review_scorecard.json`
- `runs/<id>/author_next_experiment.yaml`

Internal audit harness outputs:

- `runs/<id>/review_layers.json`
- `runs/<id>/evidence_layers.md`
- `runs/<id>/experiment_card.yaml`
- `runs/<id>/scorecard.log`

The Track 2 MVP passes if it can:

1. extract paper claims and evidence,
2. generate an ICML-style review,
3. link each weakness to a paper claim or evidence item,
4. filter off-scope criticism before review emission,
5. select exactly one next experiment for the authors.

## Generate A Review

Run:

```bash
python3 scripts/generate_see_through_review.py --paper examples/paper.md --run-id review-001
```

Then inspect:

```bash
cat runs/review-001/generated_review.md
cat runs/review-001/review_scorecard.json
```

## First Test

Run:

```bash
python3 scripts/review_see_through.py --self-test
```

This tests the internal audit harness, not the Track 2 review generator.

Then inspect:

```bash
ls runs/manual-001
cat runs/manual-001/evidence_layers.md
cat runs/manual-001/scorecard.log
```

## Detailed Evaluation

Run the deterministic labeled fixture suite:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures --run-id eval-001
```

Run the improved suite with a raw-review baseline comparison:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures --run-id eval-002
```

Run the unseen fixture suite:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen --run-id eval-003
```

Run the frozen unseen fixture suite without classifier changes:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-2 --run-id eval-004
```

Run the generalized classifier comparison on the same frozen suite:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-2 --run-id eval-005
```

Run the next frozen validation suite with grounded labels:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-006
```

Run the minimal phrase expansion on the same grounded suite:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-007
```

Evaluate Track 1-style generated-review extraction:

```bash
python3 scripts/evaluate_real_review_agent.py --fixtures fixtures-real --run-id eval-real-001
```

Prepare confirmed Track 1 paper files for human-labeled evaluation:

```bash
python3 scripts/prepare_real_paper_intake.py paper1.md paper2.md paper3.md --output fixtures-real-pending
```

Expected reports:

- `runs/<eval-id>/metrics.json`
- `runs/<eval-id>/confusion_matrix.md`
- `runs/<eval-id>/case_table.md`
- `runs/<eval-id>/scorecard.log`

## Run Archive

The normal command still writes the latest mutable report under `runs/<eval-id>/`.
Use `--archive` when the run evidence must be preserved append-only:

```bash
python3 scripts/evaluate_review_see_through.py --fixtures fixtures-unseen-3 --run-id eval-008 --archive
```

Archive mode also writes:

- `runs/archive/<timestamp>_<eval-id>/`
- `runs/current/<eval-id>.txt`
- `runs/index.jsonl`

Summarize archived runs and check archive integrity:

```bash
python3 scripts/summarize_runs.py
python3 scripts/summarize_runs.py --output runs/run_summary.md
```

## Legacy

The previous LoopCTL draft is preserved under:

```text
legacy/loopctl-v0/
```
