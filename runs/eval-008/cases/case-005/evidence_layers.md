# Evidence Layers

## Claims

- C1 (supported): The ledger links 27 generated claims to source snippets.
- C2 (supported): The evaluation uses one dataset of Auto Research traces.
- C3 (supported): No comparison against a manual claim ledger is included.

## Review Layers

### R1 - weak

The evaluation uses one dataset, so transfer to other traces is uncertain.

- targets: C1
- evidence: No deterministic fixture rule matched this criticism.
- hidden assumption: Needs LLM-assisted mapping in the next version.
- next action: Route to manual review.

### R2 - needs_experiment

It lacks a manual claim ledger baseline.

- targets: C3
- evidence: Paper claim text marks this evaluation or comparison as missing.
- hidden assumption: The missing evaluation can be turned into a bounded next-loop run.
- next action: Run the missing evaluation or comparison named by the claim.

### R3 - off_scope

The paper should add blockchain rewards for annotators.

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
