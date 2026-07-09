# Evidence Layers

## Claims

- C1 (supported): The runner builds a reproducible artifact bundle for 20 review experiments.
- C2 (supported): The bundle includes paper, review, labels, and run metadata.
- C3 (supported): No post-fallback run has been executed yet.

## Review Layers

### R1 - grounded

The paper does not run the fallback after adding the evidence bundle.

- targets: C3
- evidence: Paper states that no post-fallback run has been executed yet.
- hidden assumption: The saved fixture can evaluate the proposed fallback.
- next action: Run or dry-run the fallback on the 30-item fixture.

### R2 - weak

The bundle is only tested on 20 review experiments.

- targets: C1
- evidence: No deterministic fixture rule matched this criticism.
- hidden assumption: Needs LLM-assisted mapping in the next version.
- next action: Route to manual review.

### R3 - off_scope

The authors should optimize GPU kernel performance for the runner.

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
