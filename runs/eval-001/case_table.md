# Case Table

| case | verdict | correct/total | next experiment ok |
|---|---|---:|---|
| case-001 | PASS | 3/3 | True |
| case-002 | PASS | 3/3 | True |
| case-003 | PASS | 3/3 | True |
| case-004 | PARTIAL | 2/3 | True |
| case-005 | PASS | 3/3 | True |

## Criticism Rows

| case | criticism | expected | predicted | correct | selected next |
|---|---|---|---|---|---|
| case-001 | R1 | grounded | grounded | True | True |
| case-001 | R2 | weak | weak | True | False |
| case-001 | R3 | off_scope | off_scope | True | False |
| case-002 | R1 | contradicted | contradicted | True | False |
| case-002 | R2 | needs_experiment | needs_experiment | True | True |
| case-002 | R3 | off_scope | off_scope | True | False |
| case-003 | R1 | contradicted | contradicted | True | False |
| case-003 | R2 | needs_experiment | needs_experiment | True | True |
| case-003 | R3 | weak | weak | True | False |
| case-004 | R1 | off_scope | off_scope | True | False |
| case-004 | R2 | needs_experiment | weak | False | True |
| case-004 | R3 | weak | weak | True | False |
| case-005 | R1 | contradicted | contradicted | True | False |
| case-005 | R2 | grounded | grounded | True | True |
| case-005 | R3 | off_scope | off_scope | True | False |
