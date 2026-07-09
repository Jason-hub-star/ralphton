# ICML-Style Review: Review Patch Planner for Paper Revision Loops

## Summary
The submission presents `Review Patch Planner for Paper Revision Loops`. We propose a planner that converts peer-review comments into patch-sized revision tasks. The planner keeps unsupported requests out of the author queue and bundles each accepted task with a target claim, evidence source, and verification command.

## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Supported (E1): The planner converts 34 of 40 reviewer comments into patch-sized revision tasks.
  - E1: "The revision table reports 34 patch-sized tasks from 40 reviewer comments."
- C2 — Supported (E2): The unsupported-request filter rejects 9 of 10 off-scope review comments.
  - E2: "The filter audit reports 9 rejected off-scope review comments out of 10 unsupported requests."
- C3 — Partially supported (missing one bounded experiment) (E3): The paper suggests the planner may reduce author revision time, but no timed author study has been run.
  - E3: "The discussion says no timed author study has been run."

Weaknesses (each linked to a claim and evidence layer):
- G1 (targets C3, evidence E3): C3 is not review-ready yet: The claim is prospective, missing a direct run, or tied to an explicit limitation. Current evidence: The discussion says no timed author study has been run.
  - Hidden assumption: The paper artifact contains enough context to run a targeted validation without redesigning the method.

## Relation to Prior Works
The paper does not include a references or related-work section, so novelty claims cannot be positioned against prior work from the paper text alone.

## Other Aspects
- Originality: The contribution is narrow but concrete; originality is hard to place without verified citations.
- Significance: Significance rests on whether the central claims survive the one proposed missing experiment.
- Clarity: The paper is structured enough for claim extraction; a compact claim/evidence/limitation table would improve verifiability.

## Questions for Authors
1. For C3, can the authors run the smallest saved fixture that directly targets this claim and report claim-specific pass rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C3: The paper suggests the planner may reduce author revision time, but no timed author study has been run.
- Metric: claim-specific pass rate
- Keep when: claim-specific pass rate passes on a held-out fixture and the evidence can be reproduced from saved artifacts.
- Discard when: claim-specific pass rate fails on the held-out fixture or requires evidence not present in the paper artifacts.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
3: Weak accept anchor: 2/3 claims are supported, but 1 claim(s) still lack a direct run or direct evidence, so acceptance leans on the proposed next experiment.
