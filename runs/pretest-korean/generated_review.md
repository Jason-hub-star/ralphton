# ICML-Style Review: 한국어 리뷰 에이전트의 증거 계층 분해에 관한 연구

## Summary
The paper proposes a Korean-language review agent that decomposes each review criticism into three evidence tiers (grounded, weak, out-of-scope) by linking criticisms to specific claims using token-overlap matching. The system is evaluated on five labeled fixed cases, achieving tier accuracy 1.0, target-claim accuracy 0.93, and an out-of-scope capture rate of 1.0. The authors also report that a selector for recommending a single next experiment attains 60 percentage points higher precision than an existing method on these cases. The paper acknowledges that large-scale validation on real review corpora and extensions to mixed Korean-English reviews are left for future work.


## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Supported (E1, E7): The authors propose a review agent/pipeline that decomposes each review criticism into three evidence tiers: grounded, weak, and out-of-scope, by linking criticisms to specific claims in the paper.
  - E1: "우리는 리뷰의 각 비판을 근거 있음, 약함, 범위 밖의 세 계층으로 분류하는 파이프라인을 구축했다."
  - E7: "분류기는 토큰 중첩 기반 매칭으로 비판과 주장을 연결한다."
- C2 — Supported (E2, E3, E4, E5): On five labeled fixed cases, the proposed system achieved tier accuracy 1.0, target-claim accuracy 0.93, and an out-of-scope capture rate of 1.0.
  - E2: "다섯 개의 고정 사례에서 계층 정확도 1.0을 달성했으며, 저자에게 단 하나의 다음 실험을 제안하는 선택기가 기존 방식보다 60%p 높은 정밀도를 보였다."
  - E3: "다섯 개의 라벨링된 고정 사례에서 평가했다."
  - E4: "계층 정확도는 1.0, 타깃 주장 정확도는 0.93이었다."
  - E5: "범위 밖 포착률은 1.0을 기록했다."
- C3 — Supported (E2): The next-experiment selector that recommends a single follow-up experiment for the authors attains 60 percentage points higher precision than an existing method (on their fixed cases).
  - E2: "다섯 개의 고정 사례에서 계층 정확도 1.0을 달성했으며, 저자에게 단 하나의 다음 실험을 제안하는 선택기가 기존 방식보다 60%p 높은 정밀도를 보였다."
- C4 — Unsupported (no direct evidence found) (E2, E6): Decomposing reviews into evidence tiers helps authors trace the basis of criticisms and increases the precision of next-experiment selection.
  - E2: "다섯 개의 고정 사례에서 계층 정확도 1.0을 달성했으며, 저자에게 단 하나의 다음 실험을 제안하는 선택기가 기존 방식보다 60%p 높은 정밀도를 보였다."
  - E6: "리뷰를 증거 계층으로 분해하면 저자가 비판의 근거를 추적할 수 있고, 다음 실험 선택의 정밀도가 올라간다."
- C5 — Supported (E3, E8): A large-scale validation on a real review corpus has not yet been conducted and remains for future work.
  - E3: "다섯 개의 라벨링된 고정 사례에서 평가했다."
  - E8: "다만 대규모 실제 리뷰 코퍼스에서의 검증은 아직 수행하지 못했으며, 이는 후속 연구로 남긴다."
- C6 — Partially supported (missing one bounded experiment) (E9): The authors plan to extend their approach to a mixed Korean-English review corpus in future work.
  - E9: "향후 한국어와 영어가 혼합된 리뷰 코퍼스로 확장할 계획이다."

Weaknesses (each linked to a claim and evidence layer):
- G1 (targets C4, evidence E6, E2): The claim that decomposing reviews into evidence tiers helps authors trace the basis of criticisms and improves next-experiment selection is presented as a conclusion rather than being empirically demonstrated with user studies or explicit behavioral metrics, so the causal effect on authors remains speculative.
  - Anchored in the paper text: "리뷰를 증거 계층으로 분해하면 저자가 비판의 근거를 추적할 수 있고, 다음 실험 선택의 정밀도가 올라간다."
  - Hidden assumption: Stating that authors "can" trace criticism bases and that precision "goes up" implies a demonstrated causal effect on real users, even though no user-centric evaluation or comparison on actual author workflows is reported.
- G3 (targets C1, evidence E7): Relying solely on token-overlap-based matching to link criticisms to claims may be brittle to paraphrasing and more abstract critiques, potentially limiting the robustness of the proposed three-tier decomposition in realistic settings.
  - Anchored in the paper text: "분류기는 토큰 중첩 기반 매칭으로 비판과 주장을 연결한다."
  - Hidden assumption: Token overlap alone is sufficient to robustly capture the semantic connection between criticisms and underlying claims across the variety of linguistic expressions found in reviews.

## Relation to Prior Works
The paper does not mention or cite any prior work, so its relationship to existing literature on review analysis, argument mining, or critique linking is not discussed. As a result, it is unclear how the proposed pipeline compares conceptually or empirically to established methods in these areas.

## Other Aspects
- Originality: The idea of explicitly decomposing review criticisms into evidence tiers and linking them to claims via a simple token-overlap classifier, evaluated in the context of a Korean review corpus, appears novel within the scope of what is described.
- Significance: Given that the evaluation is limited to five fixed cases and no large-scale or user-centric validation is provided, the current demonstrated impact is modest, though the problem addressed is practically important for peer review workflows.
- Clarity: The paper is concise and clear about its pipeline, metrics, and limitations, with key components and results stated explicitly in the abstract, methods, experiments, and conclusion sections.

## Questions for Authors
1. Regarding C4 and E6, do you have any concrete plans to conduct user studies or task-based evaluations with authors to directly measure whether the tiered decomposition actually improves their ability to trace criticism bases and choose next experiments, beyond the precision metric of the selector itself?
2. For C2 and C5, have you analyzed the five labeled fixed cases in more detail (e.g., difficulty, diversity of criticism types) or considered adding even a small additional set of more varied real reviews to better understand how performance might change outside these fixed examples?
3. Concerning C6 and E9, what specific modifications do you anticipate needing in the token-overlap matching and tier assignment pipeline to handle code-switching and semantic alignment across Korean and English, and how will you empirically test that the mixed-language extension maintains high tier and claim-linking accuracy?
4. For C4, can the authors run the smallest saved fixture that directly targets this claim and report claim-specific pass rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C4: Decomposing reviews into evidence tiers helps authors trace the basis of criticisms and increases the precision of next-experiment selection.
- Metric: claim-specific pass rate
- Keep when: claim-specific pass rate passes on a held-out fixture and the evidence can be reproduced from saved artifacts.
- Discard when: claim-specific pass rate fails on the held-out fixture or requires evidence not present in the paper artifacts.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
3: Weak accept anchor: 4/6 claims are supported, but 2 claim(s) still lack a direct run or direct evidence, so acceptance leans on the proposed next experiment.
