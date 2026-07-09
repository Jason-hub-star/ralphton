# Expected Output Sketch

## Claim Cards

- C1: baseline is 27% — supported
- C2: Korean-language items are largest failure cluster — supported
- C3: fallback should improve to at least 50% — needs-experiment

## Review Audit

- R1: no fallback run — supported, targets C3
- R2: possible fixture overfit — weak, targets C3
- R3: image classification performance — not-in-paper, likely irrelevant

## Selected Experiment

```yaml
id: E1
hypothesis: "Korean-language fallback improves enrichment success rate from 27% to at least 50%."
baseline: "8/30 = 27%"
metric: "source enrichment success rate"
keep_condition: ">= 15/30 enriched and no new failure class"
discard_condition: "< 11/30 enriched or fallback causes unrelated regressions"
verify: "dry-run saved fixture with Korean fallback labels"
```

## Scorecard

```text
[2026-07-12 11:42] iter=1 claim=C3 experiment=E1 verdict=pending metric="baseline 8/30" next="run fixture dry-run"
```

