# Review See-Through Spec

## Concept

Review See-Through treats a paper review as a layered object.

The Track 2-facing agent reads a paper and writes an ICML-style review. The visible surface is review prose. The hidden structure is:

- which paper claim it targets,
- whether the criticism is grounded,
- what evidence is missing,
- what hidden assumption the reviewer made,
- what experiment would resolve the uncertainty.

The older "AI review in, audit out" scripts remain as an internal validation harness. They check whether generated or external reviews stay grounded enough for the Ralph Loop.

## Generated Review Contract

Input:

- one paper markdown file.

Output files:

- `generated_review.md`
- `evidence_layers.json`
- `review_scorecard.json`
- `author_next_experiment.yaml`

`generated_review.md` must include these ICML-style sections:

- Summary
- Strengths
- Weaknesses
- Questions for Authors
- Soundness
- Presentation
- Contribution
- Rating
- Confidence

`evidence_layers.json` must include:

- `claims`
- `evidence`
- `limitations`
- `generated_criticisms`
- `filtered_criticisms`
- `selected_next_experiment`

Each claim may also carry review-agent fields:

- `evidence_refs`
- `evidence_status`: `supported`, `needs_experiment`, or `weak`
- `rationale`

`review_scorecard.json` must include:

- `claim_count`
- `generated_criticism_count`
- `filtered_criticism_count`
- `grounded_criticism_count`
- `off_scope_filtered_count`
- `hallucination_guard_status`
- `verdict`

## Layer Labels

### grounded

The criticism is directly supported by paper text, missing evidence, or reported results.

### weak

The criticism is plausible but under-specified. It should become a missing-evidence item.

### off_scope

The criticism is not grounded in the paper or is irrelevant to the paper's claim.

### contradicted

The criticism conflicts with explicit paper evidence.

### needs_experiment

The criticism cannot be resolved by reading. It needs a bounded experiment.

## Claim Support Status

### supported

The claim has direct overlap with non-limitation evidence in the paper.

### needs_experiment

The claim is prospective, explicitly missing a run, or primarily supported by a limitation sentence.

### weak

The claim has no direct evidence sentence but is not clearly an experiment gap.

## Review Layer Object

```json
{
  "id": "R1",
  "text": "The paper claims improvement to 50% but does not run the fallback.",
  "target_claims": ["C3"],
  "layer": "grounded",
  "evidence": ["Paper states: No post-fallback run has been executed yet."],
  "hidden_assumption": "The proposed fallback can be evaluated on the saved fixture.",
  "next_action": "Run or dry-run the fallback on the 30-item fixture."
}
```

## Experiment Card

```yaml
id: E1
from_review: R1
target_claim: C3
hypothesis: "Korean-language fallback improves source enrichment success rate."
baseline: "8/30 enriched = 27%"
metric: "source enrichment success rate"
keep_condition: ">= 15/30 enriched and no new failure class"
discard_condition: "< 11/30 enriched or fallback creates unrelated regressions"
verify: "dry-run saved 30-item fixture"
```

## Output Files

The Track 2 generator writes:

### generated_review.md

Human-readable ICML-style review.

### evidence_layers.json

Machine-readable claim, evidence, limitation, criticism, filter, and next-experiment layers.

### review_scorecard.json

Compact guardrail result for one generated review.

### author_next_experiment.yaml

The next Ralph Loop input for the paper author.

The internal audit harness writes:

### review_layers.json

Machine-readable layer decomposition.

### evidence_layers.md

Human-readable audit for judges.

### experiment_card.yaml

The next Ralph Loop input.

### scorecard.log

Append-only loop trace.

## Ralph Loop Rule

One review audit chooses one experiment.

If multiple experiments look useful, choose the cheapest one that could change the review verdict.

## What Good Looks Like

Good output does not say:

> Add more experiments.

Good output says:

> Run the Korean fallback on the 30-item fixture. Keep if enrichment reaches 15/30 without a new failure class. Discard if below 11/30.
