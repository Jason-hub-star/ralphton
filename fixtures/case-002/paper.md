# Retrieval Reranker Study

## Claims

1. The BM25 baseline reaches 41% top-1 accuracy on the saved 100-query fixture.
2. The cross-encoder reranker improves top-1 accuracy to 58% on the same fixture.
3. The reranker adds 120 ms median latency per query.

## Evidence

Table 1 reports BM25 at 41% top-1 accuracy and the reranker at 58%. Table 2 reports 120 ms median latency. The paper does not include a long-tail query ablation.

