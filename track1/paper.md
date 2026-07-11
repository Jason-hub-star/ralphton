## Title

Review See-Through: Transparent Evidence Layers for Paper Review Agents

## Abstract

This paper reports measured behavior of the repository's Review See-Through
review agent, which decomposes paper-review comments into evidence layers before
choosing an author-facing next experiment. In the archived five-case harness,
the layer classifier reached 1.0 layer accuracy, 1.0 target-claim accuracy, and
1.0 off-scope catch rate across 15 criticisms. The same harness measured 1.0
precision for the see-through next-experiment selector versus 0.4 for the raw
review baseline, a 0.6 absolute gain. A separate three-case extraction
evaluation measured 1.0 accuracy or recall/precision for claim counts, claim
statuses, evidence references, limitations, and selected targets. These results
support a narrow claim: on the existing labeled harnesses, the see-through
decomposition preserves review structure, selects review targets, and improves
next-experiment selection, while downstream revision quality, broader paper
domains, and adversarial reviews remain untested.

## Claims

1. On the archived five-case harness, Review See-Through classified review evidence layers with 1.0 layer accuracy across 15 criticisms.
2. On the same archived harness, Review See-Through selected the target claim with 1.0 accuracy and caught off-scope criticisms at a 1.0 rate.
3. On the archived harness, the see-through next-experiment selector reached 1.0 precision while the raw-review baseline reached 0.4 precision, giving a 0.6 absolute gain.
4. On the three-case real extraction evaluation, the system achieved 1.0 claim-status accuracy, 1.0 evidence-reference recall, and 1.0 evidence-reference precision.
5. On the three-case real extraction evaluation, Review See-Through achieved 1.0 limitation recall and 1.0 selected-target accuracy.
6. Review See-Through will maintain at least 0.9 next-experiment precision on a larger cross-domain paper set of at least 20 cases (needs experiment).

## Evidence

The evidence below cites only repository metrics files under `runs/` and uses
the exact numeric values present in those JSON records.

| claim | metric | value | source |
| --- | --- | --- | --- |
| 1 | layer_accuracy | 1.0 | runs/archive/20260711T212137_eval-012/metrics.json#layer_accuracy |
| 1 | criticism_count | 15 | runs/archive/20260711T212137_eval-012/metrics.json#criticism_count |
| 2 | target_claim_accuracy | 1.0 | runs/archive/20260711T212137_eval-012/metrics.json#target_claim_accuracy |
| 2 | off_scope_catch_rate | 1.0 | runs/archive/20260711T212137_eval-012/metrics.json#off_scope_catch_rate |
| 3 | next_experiment_precision | 1.0 | runs/archive/20260711T212137_eval-012/metrics.json#next_experiment_precision |
| 3 | raw_next_experiment_precision | 0.4 | runs/archive/20260711T212137_eval-012/metrics.json#raw_next_experiment_precision |
| 3 | see_through_next_experiment_gain | 0.6 | runs/archive/20260711T212137_eval-012/metrics.json#see_through_next_experiment_gain |
| 4 | claim_status_accuracy | 1.0 | runs/eval-real-001/metrics.json#claim_status_accuracy |
| 4 | evidence_ref_recall | 1.0 | runs/eval-real-001/metrics.json#evidence_ref_recall |
| 4 | evidence_ref_precision | 1.0 | runs/eval-real-001/metrics.json#evidence_ref_precision |
| 5 | limitation_recall | 1.0 | runs/eval-real-001/metrics.json#limitation_recall |
| 5 | selected_target_accuracy | 1.0 | runs/eval-real-001/metrics.json#selected_target_accuracy |

## Limitations

- The strongest next-experiment result comes from a five-case archived harness, so the measured gain may not hold on larger or more diverse paper sets.
- The extraction evaluation covers three cases and reports parser-facing metrics rather than downstream author revision quality.
- The untested cross-domain precision claim is intentionally marked as needing an experiment and should not be treated as established evidence.
