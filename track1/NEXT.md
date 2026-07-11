# Next Loop Cycle

Source: `runs/track1-review-002/author_next_experiment.yaml`

Run the smallest saved held-out fixture that directly targets Claim 6: whether
Review See-Through maintains at least 0.9 next-experiment precision on a larger
cross-domain paper set of at least 20 cases.

Expected metric: `claim-specific pass rate`.

Keep the claim if the `claim-specific pass rate` passes on the held-out fixture
and the evidence can be reproduced from saved artifacts.

Discard or revise the claim if the `claim-specific pass rate` fails on the
held-out fixture or requires evidence not present in the paper artifacts.
