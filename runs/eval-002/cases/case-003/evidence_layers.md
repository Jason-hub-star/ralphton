# Evidence Layers

## Claims

- C1 (supported): The compressed prompt reduces average prompt tokens from 2400 to 900.
- C2 (supported): The compressed prompt preserves task success on the local 20-task benchmark.
- C3 (supported): The compressed prompt has not been tested on multi-file refactors.

## Review Layers

### R1 - contradicted

The paper does not report token counts, making the compression claim impossible to inspect.

- targets: C1
- evidence: Paper explicitly reports token counts before and after compression.
- hidden assumption: Reviewer missed the token count table.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

Multi-file refactor behavior is unknown and must be tested.

- targets: C3
- evidence: Paper lists multi-file refactors as future work.
- hidden assumption: A small multi-file refactor fixture can be prepared.
- next action: Run the compressed prompt on a multi-file refactor fixture.

### R3 - weak

The benchmark may be too small to show rare failures.

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
