# Evidence Layers

## Claims

- C1 (supported): The verifier preserves 31 of 32 citation links after trace compression.
- C2 (supported): The paper includes a retrieval-only baseline in Appendix A.
- C3 (supported): It has not been evaluated on multilingual papers.

## Review Layers

### R1 - contradicted

The review claims there is no retrieval-only baseline, so the verifier may not beat a simple method.

- targets: C2
- evidence: Paper claim text reports the item that the review says is absent.
- hidden assumption: Reviewer missed or discounted an explicit paper claim.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

The artifact is only tested in English papers and skips multilingual papers.

- targets: C3
- evidence: Paper claim text marks this evaluation or comparison as missing.
- hidden assumption: The missing evaluation can be turned into a bounded next-loop run.
- next action: Run the missing evaluation or comparison named by the claim.

### R3 - off_scope

The authors should add a 3D citation graph viewer.

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
