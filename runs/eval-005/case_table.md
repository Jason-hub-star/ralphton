# Case Table

| case | verdict | correct/total | see-through next ok | raw first-criticism ok |
|---|---|---:|---|---|
| case-001 | PASS | 3/3 | True | False |
| case-002 | PASS | 3/3 | True | False |
| case-003 | PASS | 3/3 | True | False |
| case-004 | PASS | 3/3 | True | False |
| case-005 | PASS | 3/3 | True | False |

## Criticism Rows

| case | criticism | expected | predicted | correct | target claims ok | see-through selected | raw selected |
|---|---|---|---|---|---|---|---|
| case-001 | R1 | contradicted | contradicted | True | True | False | True |
| case-001 | R2 | needs_experiment | needs_experiment | True | True | True | False |
| case-001 | R3 | off_scope | off_scope | True | True | False | False |
| case-002 | R1 | contradicted | contradicted | True | True | False | True |
| case-002 | R2 | needs_experiment | needs_experiment | True | True | True | False |
| case-002 | R3 | weak | weak | True | False | False | False |
| case-003 | R1 | contradicted | contradicted | True | True | False | True |
| case-003 | R2 | needs_experiment | needs_experiment | True | True | True | False |
| case-003 | R3 | off_scope | off_scope | True | True | False | False |
| case-004 | R1 | contradicted | contradicted | True | True | False | True |
| case-004 | R2 | needs_experiment | needs_experiment | True | True | True | False |
| case-004 | R3 | off_scope | off_scope | True | True | False | False |
| case-005 | R1 | contradicted | contradicted | True | True | False | True |
| case-005 | R2 | needs_experiment | needs_experiment | True | True | True | False |
| case-005 | R3 | weak | weak | True | True | False | False |
