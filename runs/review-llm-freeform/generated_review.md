# ICML-Style Review: Adaptive Retry Budgets for Tool-Using Agents

## Summary
The paper proposes an adaptive retry budget controller for tool-using language agents that reallocates retry tokens from stable to flaky tools based on per-tool failure rates and a shared retry pool.
On an internal harness of 25 recorded agent sessions, this controller reduces wasted retry tokens by 41% relative to a fixed three-retry baseline while maintaining the same task success rate of 23 out of 25 fixtures.
The implementation is described as a lightweight 180-line Python module with a replay harness for offline evaluation.
The authors suggest the approach may transfer to multi-agent settings but have not yet evaluated this or latency under bursty failure patterns.

## Claims and Evidence
Each central claim, its substantiation status, and the verbatim evidence it rests on:
- C1 — Unsupported (no direct evidence found) (E1): Tool-using language agents spend a large fraction of their token budget retrying after transient tool failures.
  - E1: "Tool-using language agents waste a large share of their token budget on retries after transient tool failures."
- C2 — Supported (E2, E4, E5, E6, E7): The proposed adaptive retry budget reallocates retry tokens from stable tools to flaky tools at runtime using per-tool failure-rate tracking and a shared retry pool, while keeping the global retry ceiling unchanged and running in constant time per call.
  - E2: "We propose an adaptive retry budget that reallocates retry tokens from stable tools to flaky tools at runtime."
  - E4: "The controller tracks a per-tool failure rate over a sliding window of 50 calls."
  - E5: "Tools whose failure rate stays under 2% surrender half of their retry budget to a shared pool."
  - E6: "Flaky tools draw from the shared pool first, so the global retry ceiling is unchanged."
  - E7: "The reallocation step runs in constant time per call."
- C3 — Supported (E3, E9, E10): On the internal harness, the adaptive retry budget reduces wasted retry tokens by about 41% compared to a fixed three-retry baseline while maintaining the same task success rate of 23 out of 25 fixtures.
  - E3: "On our internal harness the adaptive budget reduces wasted retry tokens by 41% compared with a fixed three-retry policy, while task success stays at 23 out of 25 fixtures."
  - E9: "Across 25 recorded agent sessions, the adaptive budget reduces wasted retry tokens by 41% relative to the fixed policy baseline."
  - E10: "Task success is 23 out of 25 fixtures for both policies."
- C4 — Supported (E8): The controller has a simple, lightweight implementation: 180 lines of Python with no external dependencies, and it includes a replay harness for offline evaluation.
  - E8: "The controller is 180 lines of Python with no external dependencies and ships with a replay harness for offline evaluation."
- C5 — Supported (E9): The empirical evaluation of the adaptive retry budget is based on 25 recorded agent sessions.
  - E9: "Across 25 recorded agent sessions, the adaptive budget reduces wasted retry tokens by 41% relative to the fixed policy baseline."
- C6 — Partially supported (missing one bounded experiment) (E11, E12): The same adaptive retry controller might transfer to multi-agent settings, but this has not yet been tested and would require additional experiments, including evaluation of latency under bursty failure patterns.
  - E11: "We believe the same controller could transfer to multi-agent settings, although no multi-agent run has been executed yet."
  - E12: "The limitation section says no live multi-agent test has been run, and latency under bursty failure patterns was not evaluated."

Weaknesses (each linked to a claim and evidence layer):
- G1 (targets C1, evidence E1): The claim that tool-using language agents "waste a large share" of tokens on retries is not quantitatively supported, making it difficult to judge the true practical importance of the problem being addressed. The paper does not provide any empirical measurements or concrete fractions of token budgets devoted to retries, nor does it characterize how common or severe such transient tool failures are across different settings, which weakens the motivation for the proposed controller.
  - Anchored in the paper text: "Tool-using language agents waste a large share of their token budget on retries after transient tool failures."
  - Hidden assumption: The fraction of tokens spent on retries is large enough in typical deployments to materially impact performance and justify specialized retry-budget controllers.
- G2 (targets C3, evidence E3, E9, E10): The reported 41% reduction in wasted retry tokens and unchanged success rate are based on only 25 recorded agent sessions, without any statistical analysis or breakdown across tools or scenarios, leaving uncertainty about robustness and generalizability. Additional experiments with more sessions, variance estimates, and ablations (e.g., varying the window size or threshold) would be needed to establish how stable these gains are and under what conditions they hold.
  - Anchored in the paper text: "Across 25 recorded agent sessions, the adaptive budget reduces wasted retry tokens by 41% relative to the fixed policy baseline."
  - Hidden assumption: Performance on 25 recorded agent sessions is representative of broader real-world usage and sufficient to conclude a consistent 41% reduction in wasted retry tokens.
- G3 (targets C5, evidence E9): The evaluation is limited to 25 recorded agent sessions, which is a small sample size for drawing strong conclusions about the controller’s effectiveness across diverse tools and failure modes. Without more extensive experimentation or diversity of scenarios, it is unclear whether the observed improvements would persist in other environments or under more adversarial or varied failure patterns.
  - Anchored in the paper text: "Across 25 recorded agent sessions, the adaptive budget reduces wasted retry tokens by 41% relative to the fixed policy baseline."
  - Hidden assumption: A small set of 25 recorded sessions adequately captures the range of behaviors and failure conditions relevant to deployment scenarios.
- G4 (targets C6, evidence E11, E12): The suggestion that the controller could transfer to multi-agent settings is speculative and not supported by any experiments, particularly given that latency under bursty failure patterns has not been evaluated. Concrete multi-agent trials and stress tests under correlated or bursty tool failures would be required to validate this extension.
  - Anchored in the paper text: "We believe the same controller could transfer to multi-agent settings, although no multi-agent run has been executed yet."
  - Hidden assumption: The behavior of the retry-budget controller in single-agent settings will carry over to multi-agent systems without introducing new failure modes, interactions, or latency issues.

## Relation to Prior Works
The paper does not cite or discuss any prior work on retry policies, tool-using agents, or related control mechanisms, so its relationship to existing literature is unclear.
As a result, it is not possible to assess from the text alone whether the method is building on, contrasting with, or outperforming known techniques.

## Other Aspects
- Originality: Within the scope of what is written, the idea of adaptively reallocating retry budgets among tools based on observed failure rates appears novel, though the absence of citations makes this difficult to situate in context.
- Significance: If the reported 41% reduction in wasted retry tokens with unchanged success rate generalizes beyond the small internal harness, the method could offer a practical efficiency improvement for tool-using language agents, but the limited evaluation constrains claims of broader impact.
- Clarity: The paper clearly and succinctly describes the controller’s mechanism, parameters, and reported results, but omits important experimental details and context about prior work.

## Questions for Authors
1. Regarding C1 and E1, can you provide quantitative measurements (e.g., percentage of tokens or absolute token counts) from your internal harness or other deployments to substantiate the claim that agents "waste a large share" of their token budget on retries?
2. Regarding C3 and C5 (E3, E9, E10), could you report variance or confidence intervals over the 25 recorded sessions, and possibly expand the dataset, to show how stable the 41% reduction in wasted retry tokens and 23/25 success rate are across different tools and scenarios?
3. Regarding C6 (E11, E12), do you plan specific experiments for multi-agent settings and bursty failure patterns (e.g., workloads, metrics, and scales), and can you outline any hypothesized failure modes or contention effects that might arise when multiple agents draw from the same retry-budget pool?
4. For C3, can the authors run the smallest saved fixture that directly targets this claim and report success rate, judged against the stated keep/discard condition below?

Proposed next experiment (keep/discard contract):
- Hypothesis: A bounded experiment can resolve whether the paper's evidence supports C3: On the internal harness, the adaptive retry budget reduces wasted retry tokens by about 41% compared to a fixed three-retry baseline while maintaining the same task success rate of 23 out of 25 fixtures.
- Metric: success rate
- Keep when: success rate reaches the stated target 41% without introducing a new contradiction.
- Discard when: success rate remains below 41% or the run cannot be reproduced.

## Ethical Issues
No ethical concerns were identified from the paper text.

## Overall Recommendation
3: Weak accept anchor: 4/6 claims are supported, but 2 claim(s) still lack a direct run or direct evidence, so acceptance leans on the proposed next experiment.
