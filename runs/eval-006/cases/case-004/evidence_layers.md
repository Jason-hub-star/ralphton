# Evidence Layers

## Claims

- C1 (supported): The comparator ranks evidence-backed review comments above style-only comments in 13 of 15 cases.
- C2 (supported): It includes a first-criticism raw review baseline.
- C3 (supported): It has not been tested on rebuttal-stage reviews.

## Review Layers

### R1 - contradicted

The paper omits a first-criticism raw review baseline.

- targets: C2
- evidence: Paper claim text reports the item that the review says is absent.
- hidden assumption: Reviewer missed or discounted an explicit paper claim.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

Rebuttal-stage reviews have not been tested.

- targets: C3
- evidence: Paper claim text marks this evaluation or comparison as missing.
- hidden assumption: The missing evaluation can be turned into a bounded next-loop run.
- next action: Run the missing evaluation or comparison named by the claim.

### R3 - off_scope

The comparator should add satellite image classification as a robustness task.

- targets: none
- evidence: Review request is outside the paper's stated research claim or scope.
- hidden assumption: Reviewer imported a requirement from a different task.
- next action: Ignore for this loop unless the paper adds image inputs.

## Selected Experiment

- id: E1
- from review: R2
- target claim: C3
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
