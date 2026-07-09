# Evidence Layers

## Claims

- C1 (supported): The draft generator produces section-complete paper artifacts for 9 of 10 seed ideas.
- C2 (supported): The quality gate reports word-count normalization before comparing reviewer scores.
- C3 (supported): No human preference study has been run.

## Review Layers

### R1 - contradicted

The paper omits word-count normalization, making the score comparison unfair.

- targets: C2
- evidence: Paper explicitly reports word-count normalization.
- hidden assumption: Reviewer missed the normalization statement.
- next action: Do not spend the next loop on this criticism.

### R2 - grounded

The paper does not test whether human reviewers prefer the generated papers.

- targets: C3
- evidence: Paper explicitly says no human preference study has been run.
- hidden assumption: Preference quality requires human judgment, not only artifact completeness.
- next action: Run a small human preference study.

### R3 - off_scope

The authors should add audio narration for every generated paper.

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
