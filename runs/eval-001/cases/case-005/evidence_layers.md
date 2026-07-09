# Evidence Layers

## Claims

- C1 (supported): Selecting the cheapest decisive experiment reduces wasted loop iterations.
- C2 (supported): In the saved 12-review fixture, the selector avoids 4 off-scope reviewer requests.
- C3 (supported): The selector has not been evaluated with live LLM-generated reviews.

## Review Layers

### R1 - contradicted

The selector never demonstrates that it avoids off-scope reviewer requests.

- targets: C2
- evidence: Paper reports a fixture where off-scope reviewer requests are avoided.
- hidden assumption: Reviewer missed the fixture result.
- next action: Do not spend the next loop on this criticism.

### R2 - grounded

The live LLM-generated review setting remains untested and needs a run.

- targets: C3
- evidence: Paper explicitly says no live LLM-generated review test has been run.
- hidden assumption: The same selector can be evaluated on live generated reviews.
- next action: Run the selector on a small live LLM-generated review fixture.

### R3 - off_scope

The paper should add a 3D visualization dashboard before claiming loop efficiency.

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
