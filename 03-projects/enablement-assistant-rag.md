# Project: Enablement Assistant RAG

## Problem

Personal notes and project docs pile up quickly. A small RAG assistant can answer from a trusted notebook instead of guessing from general model knowledge.

## Goal

Build a small RAG assistant that answers from a curated document set and shows the sources used.

## What This Proves

- RAG design.
- Grounded answers.
- Source traceability.
- Retrieval troubleshooting.
- Clear explanation of AI app architecture.

## Minimal Scope

- Markdown document corpus.
- Chunking and metadata.
- Embeddings.
- Retrieval.
- Answer generation with citations.
- "Not found in sources" behavior.

## Demo Script

1. Ask a question directly answered in the corpus.
2. Ask a question requiring multiple sources.
3. Ask a question not covered by the corpus.
4. Show retrieved chunks before final answer.
5. Explain one retrieval failure and how to debug it.

## Demo Talking Points

- RAG improves grounding but does not guarantee truth.
- Retrieval quality is often the bottleneck.
- Source metadata makes answers auditable.
- Evaluation needs test questions, expected sources, and expected answer traits.
