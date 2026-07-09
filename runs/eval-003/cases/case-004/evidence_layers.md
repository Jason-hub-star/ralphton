# Evidence Layers

## Claims

- C1 (supported): The router filters rubric-irrelevant comments in 8 of 10 synthetic reviews.
- C2 (supported): The paper reports a calibration curve over confidence buckets.
- C3 (supported): The evaluation has not been run with adversarial reviewer personas.

## Review Layers

### R1 - off_scope

The paper ignores visual camera calibration for the review router.

- targets: none
- evidence: Review request is outside the paper's stated research claim or scope.
- hidden assumption: Reviewer imported a requirement from a different task.
- next action: Ignore for this loop unless the paper adds image inputs.

### R2 - needs_experiment

It has not been tested with adversarial reviewer personas.

- targets: C3
- evidence: Paper says adversarial reviewer personas have not been run.
- hidden assumption: Adversarial reviewer styles may change routing behavior.
- next action: Run the router on adversarial reviewer personas.

### R3 - contradicted

The paper provides no calibration curve.

- targets: C2
- evidence: Paper explicitly reports a calibration curve.
- hidden assumption: Reviewer missed a reported calibration artifact.
- next action: Do not spend the next loop on this criticism.

## Selected Experiment

- id: E1
- from review: R2
- target claim: C3
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
