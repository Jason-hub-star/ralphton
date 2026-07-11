# Real Fixture Case Table

| case | verdict | claim count | status acc | evidence recall | evidence precision | limitation recall | selected target ok |
|---|---|---|---:|---:|---:|---:|---|
| case-001 | PASS | True | 1.0000 | 1.0000 | 1.0000 | 1.0000 | True |
| case-002 | PASS | True | 1.0000 | 1.0000 | 1.0000 | 1.0000 | True |
| case-003 | PASS | True | 1.0000 | 1.0000 | 1.0000 | 1.0000 | True |

## Claim Rows

| case | claim | expected status | predicted status | status ok | expected refs | predicted refs | refs ok |
|---|---|---|---|---|---|---|---|
| case-001 | C1 | supported | supported | True | E1 | E1 | True |
| case-001 | C2 | supported | supported | True | E2 | E2 | True |
| case-001 | C3 | needs_experiment | needs_experiment | True | E3 | E3 | True |
| case-002 | C1 | supported | supported | True | E1 | E1 | True |
| case-002 | C2 | supported | supported | True | E2 | E2 | True |
| case-002 | C3 | needs_experiment | needs_experiment | True | E3 | E3 | True |
| case-003 | C1 | supported | supported | True | E1 | E1 | True |
| case-003 | C2 | supported | supported | True | E2 | E2 | True |
| case-003 | C3 | needs_experiment | needs_experiment | True | E3 | E3 | True |
