# ICML-Style Review: Review See-Through: Transparent Evidence Layers for Paper Review Agents

## Summary
The paper introduces Review See-Through, a review agent that decomposes reviewer comments into evidence layers and then selects concrete next experiments for authors. Using a five-case archived harness, it reports perfect (1.0) performance on layer classification, target-claim selection, and off-scope detection, as well as a large precision gain in next-experiment selection over a raw-review baseline. A separate three-case extraction evaluation shows perfect accuracy/recall/precision on several parser-facing metrics, including claim status, evidence references, limitations, and selected targets. The authors explicitly position their contributions as a narrow, harness-based validation and leave cross-domain generalization and downstream author revision quality as future work.

## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Supported (E1, E5): On the archived five-case harness, Review See-Through classified review evidence layers with perfect (1.0) layer accuracy across 15 criticisms.
  - E1: "In the archived five-case harness, the layer classifier reached 1.0 layer accuracy, 1.0 target-claim accuracy, and 1.0 off-scope catch rate across 15 criticisms."
  - E5: "1. On the archived five-case harness, Review See-Through classified review evidence layers with 1.0 layer accuracy across 15 criticisms."
- C2 — Supported (E1, E6): On the same archived harness, Review See-Through selected the target claim with perfect (1.0) accuracy and caught all off-scope criticisms (1.0 catch rate).
  - E1: "In the archived five-case harness, the layer classifier reached 1.0 layer accuracy, 1.0 target-claim accuracy, and 1.0 off-scope catch rate across 15 criticisms."
  - E6: "2. On the same archived harness, Review See-Through selected the target claim with 1.0 accuracy and caught off-scope criticisms at a 1.0 rate."
- C3 — Supported (E2, E7, E11): On the archived harness, the see-through next-experiment selector achieved 1.0 precision versus 0.4 for the raw-review baseline, an absolute gain of 0.6.
  - E2: "The same harness measured 1.0 precision for the see-through next-experiment selector versus 0.4 for the raw review baseline, a 0.6 absolute gain."
  - E7: "3. On the archived harness, the see-through next-experiment selector reached 1.0 precision while the raw-review baseline reached 0.4 precision, giving a 0.6 absolute gain."
  - E11: "- The strongest next-experiment result comes from a five-case archived harness, so the measured gain may not hold on larger or more diverse paper sets."
- C4 — Supported (E3, E8, E9, E12): On the three-case real extraction evaluation, Review See-Through achieved perfect (1.0) accuracy/recall/precision for claim-status, evidence references, limitations, and selected targets.
  - E3: "A separate three-case extraction evaluation measured 1.0 accuracy or recall/precision for claim counts, claim statuses, evidence references, limitations, and selected targets."
  - E8: "4. On the three-case real extraction evaluation, the system achieved 1.0 claim-status accuracy, 1.0 evidence-reference recall, and 1.0 evidence-reference precision."
  - E9: "5. On the three-case real extraction evaluation, Review See-Through achieved 1.0 limitation recall and 1.0 selected-target accuracy."
  - E12: "- The extraction evaluation covers three cases and reports parser-facing metrics rather than downstream author revision quality."
- C5 — Supported (E4): On the existing labeled harnesses, the see-through decomposition preserves review structure, selects review targets, and improves next-experiment selection.
  - E4: "These results support a narrow claim: on the existing labeled harnesses, the see-through decomposition preserves review structure, selects review targets, and improves next-experiment selection, while downstream revision quality, broader paper domains, and adversarial reviews remain untested."
- C6 — Partially supported (missing one bounded experiment) (E10, E11, E13): Review See-Through will maintain at least 0.9 next-experiment precision on a larger cross-domain paper set of at least 20 cases.
  - E10: "6. Review See-Through will maintain at least 0.9 next-experiment precision on a larger cross-domain paper set of at least 20 cases (needs experiment)."
  - E11: "- The strongest next-experiment result comes from a five-case archived harness, so the measured gain may not hold on larger or more diverse paper sets."
  - E13: "- The untested cross-domain precision claim is intentionally marked as needing an experiment and should not be treated as established evidence."

Weaknesses (each linked to a claim and evidence layer):
- No grounded weakness survived the off-scope filter.

## Relation to Prior Works
The paper does not mention or cite any prior work, so its relation to existing systems for structured peer review analysis or experiment suggestion remains unspecified. As a result, it is hard to position Review See-Through relative to alternative review agents or information extraction tools that might already exist.

## Other Aspects
- Originality: Given the absence of cited related work, the idea of explicitly decomposing reviews into evidence layers to drive next-experiment selection appears novel within the scope of what is described here, though its originality relative to the broader literature is unclear.
- Significance: The reported metrics on small, labeled harnesses suggest potential for more reliable next-experiment suggestions, but the limited scale and lack of downstream evaluation constrain the current practical impact.
- Clarity: The claims, metrics, and limitations are stated clearly and quantitatively, with explicit acknowledgment of the narrow evaluation scope and untested generalization claims.

## Questions for Authors
1. For Claim C6 (E10, E13), can you elaborate on the planned experimental design for the larger cross-domain paper set (e.g., domains covered, sampling strategy, and annotation protocol) that would test whether the 0.9 next-experiment precision target is realistic?
2. For the archived five-case harness underpinning Claims C1–C3 (E1, E2, E5–E7), what kinds of papers and reviews were included, and how were the criticisms and target claims selected or annotated to avoid overfitting to a very specific review style?
3. For the broader claim about preserving review structure and improving next-experiment selection on existing harnesses (C5; E3, E4, E12), do you have plans to measure downstream author revision quality (e.g., via human studies or iterative revision experiments), and if so, what concrete metrics or protocols are you considering?
4. For C6, can the authors run the smallest saved fixture that directly targets this claim and report claim-specific pass rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C6: Review See-Through will maintain at least 0.9 next-experiment precision on a larger cross-domain paper set of at least 20 cases.
- Metric: claim-specific pass rate
- Keep when: claim-specific pass rate passes on a held-out fixture and the evidence can be reproduced from saved artifacts.
- Discard when: claim-specific pass rate fails on the held-out fixture or requires evidence not present in the paper artifacts.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
4: Accept anchor: 5/6 claims are directly supported; the remaining 1 claim(s) are gated by one bounded, well-specified missing experiment.
