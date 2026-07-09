# Expected Review See-Through Output

## Claim Layer

- C1: baseline is 27% — supported
- C2: Korean-language items are the largest failure cluster — supported
- C3: fallback should improve to at least 50% — needs experiment

## Review Layers

- R1: "does not run the fallback" — grounded, targets C3
- R2: "may overfit to a single fixture" — weak, targets C3
- R3: "ignores image classification performance" — off_scope, targets none

## Hidden Assumptions

- R1 assumes the saved fixture can evaluate the fallback.
- R2 assumes another fixture or split is needed before generalization can be trusted.
- R3 assumes the paper is about image classification, which it is not.

## Selected Next Experiment

```yaml
id: E1
from_review: R1
target_claim: C3
hypothesis: "Korean-language fallback improves source enrichment success rate."
baseline: "8/30 enriched = 27%"
metric: "source enrichment success rate"
keep_condition: ">= 15/30 enriched and no new failure class"
discard_condition: "< 11/30 enriched or fallback creates unrelated regressions"
verify: "dry-run saved 30-item fixture"
```

## Scorecard

```text
[timestamp] run=manual-001 criticisms=3 grounded=1 weak=1 off_scope=1 experiment=E1 verdict=ready-for-next-loop
```

