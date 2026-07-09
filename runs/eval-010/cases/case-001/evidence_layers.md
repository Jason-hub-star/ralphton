# Evidence Layers

## Claims

- C1 (supported): The selector rejects unsupported reviewer requests in 11 of 12 synthetic review fixtures.
- C2 (supported): The selector keeps every criticism tied to an explicit paper limitation.
- C3 (supported): No live LLM-generated review test has been run.

## Review Layers

### R1 - grounded

The selector has not been tried on live LLM-generated reviews.

- targets: C3
- evidence: Paper explicitly says no live LLM-generated review test has been run.
- hidden assumption: The same selector can be evaluated on live generated reviews.
- next action: Run the selector on a small live LLM-generated review fixture.

### R2 - contradicted

The review says there is no evidence that explicit paper limitations are preserved.

- targets: C2
- evidence: Paper claim text reports the item that the review says is absent.
- hidden assumption: Reviewer missed or discounted an explicit paper claim.
- next action: Do not spend the next loop on this criticism.

### R3 - off_scope

The system should include a mobile app dashboard for reviewers.

- targets: none
- evidence: Review request is outside the paper's stated research claim or scope.
- hidden assumption: Reviewer imported a requirement from a different task.
- next action: Ignore for this loop unless the paper adds image inputs.

## Selected Experiment

- id: E1
- from review: R1
- target claim: C3
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
