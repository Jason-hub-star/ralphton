# Retrieval Trace Scientist

## Title

Retrieval Trace Scientist for Auto Research Source Recovery

## Abstract

We build an agent that turns failed source-recovery traces into a ranked next-query plan. The system clusters failed retrieval attempts, chooses one repair query per cluster, and emits a reproducible run packet for the author agent.

## Claims

1. The trace scientist clusters 48 failed source-recovery attempts into 6 recurring failure modes.
2. The ranked repair plan improves source recovery from 31% to 54% on the saved 48-item fixture.
3. The method has not been tested on live post-deadline news queries.

## Evidence

The trace audit table lists 48 failed source-recovery attempts and groups them into 6 recurring failure modes.
The replay run recovers 26 of 48 items after ranked repair queries, compared with 15 of 48 items in the baseline run.
The limitation note says live post-deadline news queries have not been tested.

## Limitations

The method currently depends on saved trace packets. Live queries may introduce freshness drift and source churn.
