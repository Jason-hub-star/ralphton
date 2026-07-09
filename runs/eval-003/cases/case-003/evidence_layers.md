# Evidence Layers

## Claims

- C1 (supported): The harness records every tool call and exit code for 25 tool-use episodes.
- C2 (supported): The paper does not include a long-horizon task suite beyond 20 minutes.
- C3 (supported): The run log reports zero parser crashes on the fixture.

## Review Layers

### R1 - contradicted

The paper says nothing about parser crashes, so the logging layer may be broken.

- targets: C3
- evidence: Paper explicitly reports zero parser crashes.
- hidden assumption: Reviewer missed a run-log result.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

The evaluation lacks long-horizon tasks beyond 20 minutes.

- targets: C2
- evidence: Paper does not include the long-horizon task suite.
- hidden assumption: Longer tasks may expose tool-use failures hidden by short episodes.
- next action: Run a long-horizon task suite beyond 20 minutes.

### R3 - weak

The fixture count is small enough that rare tool failures may be missed.

- targets: C2
- evidence: Paper evidence is fixture-limited but not contradicted.
- hidden assumption: More cases may expose rare failures.
- next action: Defer broadening until the primary missing experiment is resolved.

## Selected Experiment

- id: E1
- from review: R2
- target claim: C2
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
