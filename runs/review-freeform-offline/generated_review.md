# ICML-Style Review: Adaptive Retry Budgets for Tool-Using Agents

## Summary
The submission presents `Adaptive Retry Budgets for Tool-Using Agents`. Tool-using language agents waste a large share of their token budget on
retries after transient tool failures. We propose an adaptive retry budget
that reallocates retry tokens from stable tools to flaky tools at runtime.
On our internal harness the adaptive budget reduces wasted retry tokens by
41% compared with a fixed three-retry policy, while task success stays at
23 out of 25 fixtures. We believe the same controller could transfer to
multi-agent settings, although no multi-agent run has been executed yet.

## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Partially supported (missing one bounded experiment) (no evidence ref): Tool-using language agents waste a large share of their token budget on
retries after transient tool failures. We propose an adaptive retry budget
that reallocates retry tokens from stable tools to flaky tools at runtime.
On our internal harness the adaptive budget reduces wasted retry tokens by
41% compared with a fixed three-retry policy, while task success stays at
23 out of 25 fixtures. We believe the same controller could transfer to
multi-agent settings, although no multi-agent run has been executed yet.

Weaknesses (each linked to a claim and evidence layer):
- G1 (targets C1, evidence C1): C1 is not review-ready yet: The claim is prospective, missing a direct run, or tied to an explicit limitation. Current evidence: Tool-using language agents waste a large share of their token budget on
retries after transient tool failures. We propose an adaptive retry budget
that reallocates retry tokens from stable tools to flaky tools at runtime.
On our internal harness the adaptive budget reduces wasted retry tokens by
41% compared with a fixed three-retry policy, while task success stays at
23 out of 25 fixtures. We believe the same controller could transfer to
multi-agent settings, although no multi-agent run has been executed yet.
  - Hidden assumption: The paper artifact contains enough context to run a targeted validation without redesigning the method.

## Relation to Prior Works
The paper does not include a references or related-work section, so novelty claims cannot be positioned against prior work from the paper text alone.

## Other Aspects
- Originality: The contribution is narrow but concrete; originality is hard to place without verified citations.
- Significance: Significance rests on whether the central claims survive the one proposed missing experiment.
- Clarity: The paper is structured enough for claim extraction; a compact claim/evidence/limitation table would improve verifiability.

## Questions for Authors
1. For C1, can the authors run the smallest saved fixture that directly targets this claim and report cross-paper transfer pass rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C1: Tool-using language agents waste a large share of their token budget on
retries after transient tool failures. We propose an adaptive retry budget
that reallocates retry tokens from stable tools to flaky tools at runtime.
On our internal harness the adaptive budget reduces wasted retry tokens by
41% compared with a fixed three-retry policy, while task success stays at
23 out of 25 fixtures. We believe the same controller could transfer to
multi-agent settings, although no multi-agent run has been executed yet.
- Metric: cross-paper transfer pass rate
- Keep when: cross-paper transfer pass rate reaches the stated target 41% without introducing a new contradiction.
- Discard when: cross-paper transfer pass rate remains below 41% or the run cannot be reproduced.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
1: Reject anchor: none of the 1 extracted claims are supported by direct evidence in the paper.
