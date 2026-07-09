# LoopCTL

Ralph Loop-native Auto Research control plane.

LoopCTL is not a one-shot paper writer or one-shot review agent. It is a small control layer that keeps an auto-research loop moving:

1. extract claims from a paper or review,
2. choose one cheap experiment,
3. run or dry-run verification,
4. record evidence,
5. decide keep/discard,
6. feed the result into the next Ralph Loop iteration.

The core bet:

> Auto Research improves when agents are forced to turn vague criticism into small, evidence-backed next experiments.

## Ralphthon Fit

Ralphthon rewards workflows that can keep running after the first draft. LoopCTL focuses on the loop itself:

- Track 1: AI Scientist uses LoopCTL to improve a paper through evidence-backed iterations.
- Track 2: Review Agent uses LoopCTL to convert review findings into verifiable next experiments.

The stronger angle is Track 2:

> Review Agent that does not stop at an ICML-style review. It audits its own review, extracts missing evidence, and creates the next experiment card.

## What Makes It Different

Existing tools review papers, check reproducibility, or ground claims. LoopCTL instead manages the research loop:

- one hypothesis at a time,
- baseline vs experiment,
- keep/discard before code or paper changes settle,
- scorecard logging,
- failure clustering,
- next-loop planning.

This comes from the local harness pattern already proven in:

- `jason-agent-harness-template/harnesses/autoresearch-loop.md`
- `jason-agent-harness-template/harnesses/evidence-review.md`
- `jason-agent-harness-template/harnesses/tiered-review.md`
- `unityctl workflow verify`
- `건설사/ralph-construction`

## MVP Output

The MVP should produce these files:

- `claim_cards.json`
- `experiment_cards/*.yaml`
- `evidence_ledger.md`
- `review_audit.md`
- `next_loop_plan.md`
- `scorecard.log`

## Minimal Demo

Use one small paper-style artifact and one review. LoopCTL should:

1. find 3 to 5 claims,
2. mark evidence status for each,
3. choose the cheapest next experiment,
4. produce an experiment card,
5. simulate or run verification,
6. write a scorecard entry,
7. produce a revised next-loop plan.

Success is not "perfect review." Success is "the next iteration is obvious, bounded, and evidence-backed."

