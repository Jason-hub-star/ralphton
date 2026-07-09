# Evidence Layers

## Claims

- C1 (supported): The compressor reduces trace tokens by 38% while keeping all reviewer-visible citations.
- C2 (supported): The paper evaluates the compressor on one local repository.
- C3 (supported): It does not compare against a no-compression review prompt.

## Review Layers

### R1 - weak

The paper relies on one repository, so transfer to other codebases is uncertain.

- targets: C2
- evidence: Paper evidence is fixture-limited but not contradicted.
- hidden assumption: More cases may expose rare failures.
- next action: Defer broadening until the primary missing experiment is resolved.

### R2 - needs_experiment

The paper lacks a no-compression prompt comparison.

- targets: C3
- evidence: Paper says no no-compression prompt comparison has been run.
- hidden assumption: Compression must beat the simplest uncompressed baseline.
- next action: Compare against a no-compression review prompt.

### R3 - off_scope

The paper should classify satellite images to prove robustness.

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
