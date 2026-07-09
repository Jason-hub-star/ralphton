# LoopCTL Test Plan

## Goal

Test whether LoopCTL can turn a paper/review pair into one concrete Ralph Loop iteration.

The first test should be tiny. Do not build a full app yet.

## Test Question

Can LoopCTL reliably convert unsupported or weak review criticism into a small experiment card with a measurable keep/discard condition?

## Test Fixture

Use a deliberately small fake paper and fake review:

- paper has 3 claims,
- review has 3 criticisms,
- one criticism is supported,
- one criticism is weak,
- one criticism is hallucinated or not grounded in the paper.

Expected result:

- LoopCTL identifies all 3 claims,
- links review criticism to paper evidence,
- flags unsupported review text,
- chooses exactly 1 next experiment,
- writes scorecard output.

## Manual Test Steps

1. Prepare fixture files:
   - `examples/paper.md`
   - `examples/review.md`
2. Create claim cards:
   - claim id
   - claim text
   - evidence quoted or referenced
   - evidence status
3. Create review audit:
   - criticism id
   - target claim id
   - grounded status
   - reason
4. Pick one next experiment:
   - cheapest experiment that would change the review verdict
5. Write experiment card:
   - hypothesis
   - baseline
   - metric
   - keep condition
   - discard condition
   - verify command or dry-run instruction
6. Write scorecard:
   - timestamp
   - selected experiment
   - verdict
   - next loop input

## Pass Criteria

The test passes if:

- exactly one next experiment is selected,
- selected experiment maps to a specific claim or criticism,
- keep/discard conditions are measurable,
- unsupported review criticism is flagged,
- scorecard can be read without opening the whole paper.

## Fail Criteria

The test fails if:

- LoopCTL generates broad advice instead of one experiment,
- no baseline is recorded,
- keep/discard is vague,
- evidence status is missing,
- the next iteration depends on human interpretation.

## 10-Hour Ralphthon Test Strategy

### Hour 0-1: Fixture and Schema

- Make `paper.md`, `review.md`, expected output examples.
- Freeze the output formats.

### Hour 1-3: Claim and Review Extraction

- Extract claims and review criticisms with simple LLM prompts.
- Avoid complex parsing.

### Hour 3-5: Evidence Ledger

- Link criticism to claim.
- Mark: `supported`, `weak`, `missing`, `contradicted`, `not-in-paper`.

### Hour 5-7: Experiment Card Generator

- Pick one next experiment.
- Require a metric and keep/discard conditions.

### Hour 7-8: Scorecard

- Append one line per iteration.
- Include enough context for judges to inspect the loop.

### Hour 8-10: Demo Run

- Run 2 to 3 iterations on the same fixture.
- Show how the loop gets sharper.

## Anti-Goals

- Do not build a full paper parser.
- Do not execute arbitrary untrusted code.
- Do not support every research domain.
- Do not optimize UI before the loop works.

