# fixtures-real

Frozen Track 1-style paper fixtures for evaluating the Track 2 Review Agent.

These are realistic local surrogate papers, not confirmed original Ralphthon Track 1 submissions. A local search did not find actual external Track 1 paper artifacts in the workspace, so these fixtures are used to test extraction behavior before replacing them with real event papers.

Each case contains:

- `paper.md`
- `labels.json`

The evaluator checks:

- claim count extraction,
- claim support status,
- evidence reference matching,
- limitation extraction,
- selected next-experiment target.
