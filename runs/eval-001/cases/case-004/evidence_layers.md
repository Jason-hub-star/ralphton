# Evidence Layers

## Claims

- C1 (supported): The review calibrator catches 6 unsupported criticisms out of 20 synthetic reviews.
- C2 (supported): The calibrator preserves all grounded criticisms in the same fixture.
- C3 (supported): The calibrator does not evaluate reviewer tone or writing style.

## Review Layers

### R1 - off_scope

The paper ignores reviewer tone, which is the key signal for review quality.

- targets: none
- evidence: Review request is outside the paper's stated research claim or scope.
- hidden assumption: Reviewer imported a requirement from a different task.
- next action: Ignore for this loop unless the paper adds image inputs.

### R2 - weak

The paper reports unsupported criticism catches but does not run on real conference reviews.

- targets: C3
- evidence: Paper states that no post-fallback run has been executed yet.
- hidden assumption: The saved fixture can evaluate the proposed fallback.
- next action: Run or dry-run the fallback on the 30-item fixture.

### R3 - weak

The preservation of grounded criticisms is supported only on synthetic reviews.

- targets: C2
- evidence: Paper evidence is fixture-limited but not contradicted.
- hidden assumption: More cases may expose rare failures.
- next action: Defer broadening until the primary missing experiment is resolved.

## Selected Experiment

- id: E1
- from review: R2
- target claim: C3
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
