# Evidence Ledger Compressor

## Title

Evidence Ledger Compressor for Long Ralph Loops

## Abstract

We introduce a compressor that turns long Ralph Loop logs into a claim ledger, a failure ledger, and one next-experiment card. The goal is to preserve enough evidence for reviewers while keeping the status page short.

## Claims

1. The compressor reduces a 19,400-token loop log to a 1,180-token curated status page.
2. The compressed status page preserves all 12 gold evidence anchors.
3. The compressor should generalize to multi-agent loops with more than three agents.

## Evidence

The token count table reports 19,400 input tokens and 1,180 output tokens for the saved loop.
The evidence-anchor audit reports 12 of 12 gold anchors preserved in the compressed status page.
No multi-agent loop with more than three agents is included in the evaluation.

## Limitations

The evaluation covers one saved loop family. Cross-loop and multi-agent generalization remain untested.
