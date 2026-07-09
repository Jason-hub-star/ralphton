# Evidence Layers

## Claims

- C1 (supported): The BM25 baseline reaches 41% top-1 accuracy on the saved 100-query fixture.
- C2 (supported): The cross-encoder reranker improves top-1 accuracy to 58% on the same fixture.
- C3 (supported): The reranker adds 120 ms median latency per query.

## Review Layers

### R1 - contradicted

The paper does not report the BM25 baseline, so the improvement claim is unsupported.

- targets: C1, C2
- evidence: Paper explicitly reports the BM25 baseline and reranker result.
- hidden assumption: Reviewer missed an explicit baseline table entry.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

The long-tail query behavior is unclear and needs an ablation.

- targets: C2
- evidence: Paper does not include a long-tail query ablation.
- hidden assumption: A long-tail slice is available or can be constructed from the fixture.
- next action: Run a long-tail query ablation.

### R3 - off_scope

The reviewer asks for a mobile app usability study before accepting the reranker.

- targets: none
- evidence: Review request is outside the paper's stated research claim or scope.
- hidden assumption: Reviewer imported a requirement from a different task.
- next action: Ignore for this loop unless the paper adds image inputs.

## Selected Experiment

- id: E1
- from review: R2
- target claim: C2
- metric: claim-specific success metric
- keep: measurable improvement or direct support for the target claim
- discard: no measurable support or new regression evidence
