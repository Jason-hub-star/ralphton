# LoopCTL Loop Spec

## Objects

### Claim Card

```yaml
id: C1
text: "The proposed method improves source recovery from 27% to at least 50%."
source:
  file: paper.md
  section: Experiments
evidence_status: weak
evidence_refs:
  - "Table 1 reports 27% baseline but no post-intervention run."
needed_evidence:
  - "Run the same benchmark after the proposed heuristic."
```

### Review Criticism

```yaml
id: R1
text: "The paper does not prove the improvement generalizes beyond one fixture."
target_claims: [C1]
grounding: supported
reason: "The paper reports one dataset only."
```

### Experiment Card

```yaml
id: E1
hypothesis: "Adding Korean-language search fallback improves source enrichment success rate."
baseline: "8/30 enriched = 27%"
scope: "fixture-only or one add-only fallback"
metric: "source enrichment success rate"
keep_condition: ">= 50% enrichment and no increase in failed calls"
discard_condition: "improvement < 10 percentage points or latency doubles"
verify: "dry-run on saved 30-item fixture"
timebox: "30m"
```

### Evidence Ledger Entry

```yaml
iteration: 1
claim: C1
experiment: E1
result: keep
evidence:
  metric_before: "27%"
  metric_after: "53%"
  notes: "Recovered Korean-language cluster."
next_input: "Update review verdict from weak evidence to partially supported."
```

## Loop Algorithm

1. Read paper and review.
2. Extract 3 to 7 major claims.
3. Extract 3 to 7 major review criticisms.
4. Link criticisms to claims.
5. Classify each criticism:
   - `supported`
   - `weak`
   - `not-in-paper`
   - `contradicted`
   - `needs-experiment`
6. Rank missing evidence by:
   - cheapest to test,
   - likely to change verdict,
   - low risk,
   - clear metric.
7. Select exactly one experiment.
8. Run or dry-run verification.
9. Write keep/discard.
10. Feed the result into the next iteration.

## Scorecard Format

Use append-only plain text.

```text
[2026-07-12 11:42] iter=1 claim=C1 experiment=E1 verdict=keep metric="27% -> 53%" next="revise evidence status"
```

## Design Rules

- One loop, one experiment.
- No vague next steps.
- No keep without evidence.
- No discard residue.
- Every review criticism must point to a claim, artifact, or missing evidence.
- If the cheapest experiment is unsafe or too broad, choose dry-run.

