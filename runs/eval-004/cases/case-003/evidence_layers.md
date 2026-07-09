# Evidence Layers

## Claims

- C1 (supported): The generator emits bounded keep and discard conditions for 14 of 15 review criticisms.
- C2 (supported): The output schema is validated by a deterministic JSON checker.
- C3 (supported): It does not test whether researchers can execute the generated cards within one day.

## Review Layers

### R1 - contradicted

The paper does not validate the output schema.

- targets: C2
- evidence: Paper claim text reports the item that the review says is absent.
- hidden assumption: Reviewer missed or discounted an explicit paper claim.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

It remains unclear whether a researcher can actually execute the generated experiment cards in one day.

- targets: C3
- evidence: Paper claim text marks this evaluation or comparison as missing.
- hidden assumption: The missing evaluation can be turned into a bounded next-loop run.
- next action: Run the missing evaluation or comparison named by the claim.

### R3 - off_scope

The paper should include a voice assistant to read the cards aloud.

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
