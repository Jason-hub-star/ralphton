# Evidence Layers

## Claims

- C1 (supported): The loop scheduler reduces idle tool time from 42 minutes to 18 minutes on 12 Auto Research tasks.
- C2 (supported): The benchmark reports the planner-only baseline and the scheduler result in Table 1.
- C3 (supported): The study leaves model-tier cost ablations for future work.

## Review Layers

### R1 - contradicted

The paper does not report the planner-only baseline, so the scheduler gain is unsupported.

- targets: C2
- evidence: Paper explicitly reports the planner-only baseline.
- hidden assumption: Reviewer missed a reported baseline.
- next action: Do not spend the next loop on this criticism.

### R2 - needs_experiment

The paper never runs model-tier cost ablations, so the chosen workflow may be uneconomical.

- targets: C3
- evidence: Paper lists model-tier cost ablations as future work.
- hidden assumption: Cost can change the preferred workflow even if quality holds.
- next action: Run a model-tier cost ablation.

### R3 - off_scope

The system should ship a mobile notification app for annotators.

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
