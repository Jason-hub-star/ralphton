# ICML-Style Review: Review Patch Planner for Paper Revision Loops

## Summary
The paper introduces a "Review Patch Planner" that converts reviewer comments into patch-sized revision tasks and filters out unsupported requests. Empirically, it reports that 34 of 40 reviewer comments are converted into patch tasks and that the unsupported-request filter rejects 9 of 10 off-scope comments. The authors also suggest that the planner might reduce author revision time, while acknowledging that this has not yet been validated with human timing studies. The current evaluation is conducted on synthetic reviewer comments and saved paper drafts rather than live interactions.

## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Supported (E1, E4): The planner converts 34 of 40 reviewer comments into patch-sized revision tasks.
  - E1: "1. The planner converts 34 of 40 reviewer comments into patch-sized revision tasks."
  - E4: "The revision table reports 34 patch-sized tasks from 40 reviewer comments."
- C2 — Supported (E2, E5): The unsupported-request filter rejects 9 of 10 off-scope review comments.
  - E2: "2. The unsupported-request filter rejects 9 of 10 off-scope review comments."
  - E5: "The filter audit reports 9 rejected off-scope review comments out of 10 unsupported requests."
- C3 — Partially supported (missing one bounded experiment) (E3, E6, E8): The planner may reduce author revision time, but this has not been validated because no timed author study or human timing evidence is available.
  - E3: "3. The paper suggests the planner may reduce author revision time, but no timed author study has been run."
  - E6: "The discussion says no timed author study has been run."
  - E8: "Human timing evidence is absent."
- C4 — Supported (E7): The current evaluation of the planner is conducted using synthetic reviewer comments and saved paper drafts rather than live human interactions.
  - E7: "The current evaluation uses synthetic reviewer comments and saved paper drafts."

Weaknesses (each linked to a claim and evidence layer):
- G2 (targets C4, evidence E7): Because the evaluation relies only on synthetic reviewer comments and saved drafts, it is unclear whether the reported performance would hold under realistic, noisy reviewer feedback and live author–reviewer interaction loops.
  - Anchored in the paper text: "The current evaluation uses synthetic reviewer comments and saved paper drafts."
  - Hidden assumption: It is assumed that synthetic reviewer comments and archived drafts faithfully capture the complexity and variability of real peer-review dynamics and author behavior.
- G3 (targets C1, evidence E1, E4): The conversion rate of 34 out of 40 reviewer comments, while promising, is based on a very small sample, raising concerns about how robust or generalizable this result is across different papers, venues, and reviewer styles.
  - Anchored in the paper text: "The revision table reports 34 patch-sized tasks from 40 reviewer comments."
  - Hidden assumption: It is assumed that a dataset of only 40 reviewer comments is large and diverse enough to provide a stable estimate of the planner’s conversion performance.

## Relation to Prior Works
The paper does not cite or describe any prior work, so its relationship to existing research on peer review tools, task planning, or automated revision assistance is unclear from the text provided.

## Other Aspects
- Originality: The idea of a planner that turns peer-review comments into structured patch-sized revision tasks with explicit targets and verification commands appears novel within the scope of what is described.
- Significance: If validated with real users, the approach could be significant for reducing friction in the revision loop by filtering unsupported requests and structuring revision tasks, but its impact remains speculative without human studies.
- Clarity: The core claims, setup, and limitations are stated clearly and succinctly, making the contribution easy to understand despite the brief description.

## Questions for Authors
1. 1. For Claim C3, do you have any preliminary anecdotal reports or small pilot observations from real authors using the planner that could guide the design of a future timed author study to validate revision-time savings?
2. 2. For Claim C4, how do you plan to adapt or validate the planner when moving from synthetic reviewer comments and saved drafts to real conference or journal review threads with diverse and sometimes conflicting reviewer feedback?
3. 3. Regarding Claim C1, can you comment on how you selected the 40 reviewer comments used in the revision table and whether you expect the 34/40 conversion rate to hold on larger, more heterogeneous sets of reviews?
4. For C4, can the authors run the smallest saved fixture that directly targets this claim and report claim-specific pass rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C4: The current evaluation of the planner is conducted using synthetic reviewer comments and saved paper drafts rather than live human interactions.
- Metric: claim-specific pass rate
- Keep when: claim-specific pass rate passes on a held-out fixture and the evidence can be reproduced from saved artifacts.
- Discard when: claim-specific pass rate fails on the held-out fixture or requires evidence not present in the paper artifacts.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
4: Accept anchor: 3/4 claims are directly supported; the remaining 1 claim(s) are gated by one bounded, well-specified missing experiment.
