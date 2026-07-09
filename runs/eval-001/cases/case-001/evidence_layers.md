# Evidence Layers

## Claims

- C1 (supported): The baseline source enrichment success rate is 27% on the saved 30-item fixture.
- C2 (supported): Korean-language items form the largest identifiable failure cluster.
- C3 (needs_experiment): A Korean-language fallback should improve enrichment success rate to at least 50%.

## Review Layers

### R1 - grounded

The paper claims improvement to 50% but does not run the fallback.

- targets: C3
- evidence: Paper states that no post-fallback run has been executed yet.
- hidden assumption: The saved fixture can evaluate the proposed fallback.
- next action: Run or dry-run the fallback on the 30-item fixture.

### R2 - weak

The paper may overfit to a single 30-item fixture.

- targets: C3
- evidence: Paper uses one 30-item fixture; generalization is not tested.
- hidden assumption: A second fixture or split would reveal generalization risk.
- next action: Add a second fixture only after the first fallback run passes.

### R3 - off_scope

The paper ignores image classification performance, which could affect the conclusion.

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
