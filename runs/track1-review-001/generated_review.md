# ICML-Style Review: Review See-Through: Transparent Evidence Layers for Paper Review Agents

## Summary
The paper introduces Review See-Through, a review agent that decomposes reviewer comments into evidence layers to support better next-experiment suggestions. On a five-case archived harness, it reports perfect (1.0) accuracy for layer classification, target-claim selection, and off-scope detection, as well as a 0.6 absolute precision gain in next-experiment selection over a raw-review baseline. A three-case extraction evaluation shows perfect parser-facing metrics for claim statuses, evidence references, limitations, and selected targets. The authors argue these results support improved next-experiment selection, while acknowledging that broader domains and downstream author impacts remain untested.

## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Supported (E1, E5): On the archived five-case harness, Review See-Through classifies review evidence layers with perfect (1.0) accuracy across 15 criticisms.
  - E1: "In the archived five-case harness, the layer classifier reached 1.0 layer accuracy, 1.0 target-claim accuracy, and 1.0 off-scope catch rate across 15 criticisms."
  - E5: "1. On the archived five-case harness, Review See-Through classified review evidence layers with 1.0 layer accuracy across 15 criticisms."
- C2 — Supported (E1, E6): On the same archived harness, Review See-Through selects the target claim with perfect accuracy and catches all off-scope criticisms.
  - E1: "In the archived five-case harness, the layer classifier reached 1.0 layer accuracy, 1.0 target-claim accuracy, and 1.0 off-scope catch rate across 15 criticisms."
  - E6: "2. On the same archived harness, Review See-Through selected the target claim with 1.0 accuracy and caught off-scope criticisms at a 1.0 rate."
- C3 — Supported (E2, E7): On the archived harness, the see-through next-experiment selector achieves 1.0 precision compared to 0.4 for the raw-review baseline, an absolute gain of 0.6.
  - E2: "The same harness measured 1.0 precision for the see-through next-experiment selector versus 0.4 for the raw review baseline, a 0.6 absolute gain."
  - E7: "3. On the archived harness, the see-through next-experiment selector reached 1.0 precision while the raw-review baseline reached 0.4 precision, giving a 0.6 absolute gain."
- C4 — Supported (E3, E8, E9): On the three-case real extraction evaluation, the system achieves perfect (1.0) accuracy or recall/precision for claim statuses, evidence references, limitations, and selected targets, including 1.0 claim-status accuracy and 1.0 evidence-reference recall and precision.
  - E3: "A separate three-case extraction evaluation measured 1.0 accuracy or recall/precision for claim counts, claim statuses, evidence references, limitations, and selected targets."
  - E8: "4. On the three-case real extraction evaluation, the system achieved 1.0 claim-status accuracy, 1.0 evidence-reference recall, and 1.0 evidence-reference precision."
  - E9: "5. Because the three-case extraction evaluation also measured 1.0 limitation recall and 1.0 selected-target accuracy, Review See-Through improves downstream author revision quality."
- C5 — Unsupported (no direct evidence found) (E4, E9, E12): Because the extraction evaluation reports perfect parsing metrics, Review See-Through improves downstream author revision quality.
  - E4: "These results support a narrow claim: on the existing labeled harnesses, the see-through decomposition preserves review structure and improves next-experiment selection, while broader paper domains and adversarial reviews remain untested."
  - E9: "5. Because the three-case extraction evaluation also measured 1.0 limitation recall and 1.0 selected-target accuracy, Review See-Through improves downstream author revision quality."
  - E12: "- The extraction evaluation covers three cases and reports parser-facing metrics rather than downstream author revision quality."
- C6 — Partially supported (missing one bounded experiment) (E4, E10, E13): Review See-Through will maintain at least 0.9 next-experiment precision on a larger, cross-domain paper set of at least 20 cases.
  - E4: "These results support a narrow claim: on the existing labeled harnesses, the see-through decomposition preserves review structure and improves next-experiment selection, while broader paper domains and adversarial reviews remain untested."
  - E10: "6. Review See-Through will maintain at least 0.9 next-experiment precision on a larger cross-domain paper set of at least 20 cases (needs experiment)."
  - E13: "- The untested cross-domain precision claim is intentionally marked as needing an experiment and should not be treated as established evidence."

Weaknesses (each linked to a claim and evidence layer):
- G1 (targets C5, evidence E9, E12): Claim C5 asserts that "Review See-Through improves downstream author revision quality" based on parser-facing metrics alone, but the paper explicitly acknowledges that downstream revision quality was not measured, creating a gap between evidence and conclusion. The limitation "- The extraction evaluation covers three cases and reports parser-facing metrics rather than downstream author revision quality." (E12) directly undercuts the causal claim in E9 that improved parsing leads to better revisions, which is not empirically demonstrated in the reported experiments. Thus the claim overreaches the established evidence and should either be weakened or supported by a dedicated user-study or revision-quality evaluation.
  - Anchored in the paper text: ""- The extraction evaluation covers three cases and reports parser-facing metrics rather than downstream author revision quality.""
  - Hidden assumption: Perfect parser-facing extraction metrics reliably translate into improved downstream author revision quality without needing to measure actual revisions.

## Relation to Prior Works
The paper does not cite any prior work or related systems, so it is not possible to assess how the approach compares to existing review-assistance tools or evaluation harnesses based on the provided text.

## Other Aspects
- Originality: The work appears original in framing review assistance as explicit evidence-layer decomposition combined with a next-experiment selector evaluated on labeled harnesses.
- Significance: Given the very small and narrow evaluation (five archived and three real cases), the potential significance is promising but currently limited to demonstrating feasibility rather than broad practical impact.
- Clarity: The paper clearly states its main claims, provides explicit metrics with references to repository files, and includes a concise limitations section that delineates the scope of the results.

## Questions for Authors
1. For Claim C5, do you have any preliminary or qualitative evidence (e.g., author feedback or revision outcomes) that links the perfect parser-facing metrics (E3, E8, E9) to actual improvements in downstream author revision quality, or is this currently a purely hypothesized benefit?
2. For Claim C6, can you outline the concrete experimental design you plan to use to test whether next-experiment precision remains at or above 0.9 on a cross-domain set of at least 20 cases, including how you will select papers and annotate ground truth (E10, E11, E13)?
3. For the next-experiment precision result in C3, could you report additional statistics (e.g., per-case performance or confidence intervals) on the five-case harness to help readers judge how sensitive the 0.6 absolute gain (E2, E7) might be to small changes in the dataset?
4. For C5, can the authors run the smallest saved fixture that directly targets this claim and report claim-specific pass rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C5: Because the extraction evaluation reports perfect parsing metrics, Review See-Through improves downstream author revision quality.
- Metric: claim-specific pass rate
- Keep when: claim-specific pass rate passes on a held-out fixture and the evidence can be reproduced from saved artifacts.
- Discard when: claim-specific pass rate fails on the held-out fixture or requires evidence not present in the paper artifacts.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
3: Weak accept anchor: 4/6 claims are supported, but 2 claim(s) still lack a direct run or direct evidence, so acceptance leans on the proposed next experiment.
