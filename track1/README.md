# Track 1 Harness — Paper-Writing Ralph Loop

The same `loop.sh` pointed at a different contract: the loop WRITES a paper,
`scripts/evaluate_track1_paper.py` deterministically checks structure and
verifies every cited number against ground truth under `runs/`, and the
Track 2 review agent reviews the result (`scripts/track1_selfreview.sh`,
recommendation-gated). The review's proposed next experiment lands in
`track1/NEXT.md` — the seed of the next loop cycle. One repo, both Ralphthon
tracks, one closed loop.

```bash
bash start.sh track1   # preflight + caffeinate; same as:
RALPH_PROMPT=track1/PROMPT.md caffeinate -is bash loop.sh --max-iterations 8
```

- New topic: edit only the Topic block and task list in `track1/TASKS.md`;
  the contract and judges stay unchanged. Use fresh run-ids in the new tasks
  so the rehearsal artifacts under `runs/track1-*` are not overwritten;
  `start.sh` refuses to launch while every task is still checked from the
  rehearsal. Naming trap: metrics the paper will CITE must live outside
  `runs/track1*` (the gate rejects those sources as self-written), so name
  experiment runs like `t1exp-...`; review/gate run-ids are unrestricted.
- Do NOT run this loop and the root Track 2 loop at the same time — both
  commit with `git add -A` in one working tree. Run them sequentially.

Artifacts: `track1/paper.md`, `runs/track1-gate-00*/track1_gate.log`,
`runs/track1-review-00*/` (ICML-form self-reviews), `track1/NEXT.md`.
