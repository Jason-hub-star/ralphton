# Evidence Layers

## Claims

- C1 (supported): The synthesizer clusters reviewer disagreements into 7 issue groups on 18 synthetic reviews.
- C2 (supported): It reports inter-annotator agreement with Cohen kappa of 0.71.
- C3 (supported): No real program committee discussion logs are used.

## Review Layers

### R1 - contradicted

The paper never reports annotator agreement, so the clusters may be arbitrary.

- targets: C2
- evidence: Paper claim text reports the item that the review says is absent.
- hidden assumption: Reviewer missed or discounted an explicit paper claim.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

The system is not checked against real PC discussion logs.

- targets: C3
- evidence: Paper claim text marks this evaluation or comparison as missing.
- hidden assumption: The missing evaluation can be turned into a bounded next-loop run.
- next action: Run the missing evaluation or comparison named by the claim.

### R3 - weak

The benchmark is based on only 18 synthetic reviews.

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
