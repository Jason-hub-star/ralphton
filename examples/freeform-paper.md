# Adaptive Retry Budgets for Tool-Using Agents

## Abstract

Tool-using language agents waste a large share of their token budget on
retries after transient tool failures. We propose an adaptive retry budget
that reallocates retry tokens from stable tools to flaky tools at runtime.
On our internal harness the adaptive budget reduces wasted retry tokens by
41% compared with a fixed three-retry policy, while task success stays at
23 out of 25 fixtures. We believe the same controller could transfer to
multi-agent settings, although no multi-agent run has been executed yet.

## Method

The controller tracks a per-tool failure rate over a sliding window of 50
calls. Tools whose failure rate stays under 2% surrender half of their retry
budget to a shared pool.

### Budget reallocation

Flaky tools draw from the shared pool first, so the global retry ceiling is
unchanged. The reallocation step runs in constant time per call.

### Implementation notes

The controller is 180 lines of Python with no external dependencies and ships
with a replay harness for offline evaluation.

## Results

Across 25 recorded agent sessions, the adaptive budget reduces wasted retry
tokens by 41% relative to the fixed policy baseline. Task success is 23 out
of 25 fixtures for both policies. The limitation section says no live
multi-agent test has been run, and latency under bursty failure patterns was
not evaluated.
