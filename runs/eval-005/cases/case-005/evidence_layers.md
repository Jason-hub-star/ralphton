# Evidence Layers

## Claims

- C1 (supported): The planner converts 11 of 13 actionable review comments into revision tasks.
- C2 (supported): It preserves all explicit reviewer constraints in the generated task list.
- C3 (supported): No comparison against a human-written revision plan is included.

## Review Layers

### R1 - contradicted

The paper gives no evidence that reviewer constraints are preserved.

- targets: C2
- evidence: Paper claim text reports the item that the review says is absent.
- hidden assumption: Reviewer missed or discounted an explicit paper claim.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

It lacks a human-written revision plan baseline.

- targets: C3
- evidence: Paper claim text marks this evaluation or comparison as missing.
- hidden assumption: The missing evaluation can be turned into a bounded next-loop run.
- next action: Run the missing evaluation or comparison named by the claim.

### R3 - weak

The conversion audit has only 13 actionable comments.

- targets: C1
- evidence: No deterministic fixture rule matched this criticism.
- hidden assumption: Needs LLM-assisted mapping in the next version.
- next action: Route to manual review.

## Selected Experiment

- id: E1
- from review: R2
- target claim: C3
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
