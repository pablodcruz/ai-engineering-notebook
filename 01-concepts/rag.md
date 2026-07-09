# Retrieval-Augmented Generation

## Why This Matters

Explain how RAG lets an AI application answer using external knowledge without putting all knowledge into the model itself.

## Core Explanation

RAG retrieves relevant content from a knowledge source and passes that content into the model as grounding context. The model then generates an answer using the retrieved material.

## Basic Flow

1. Ingest documents.
2. Split content into chunks.
3. Create embeddings for chunks.
4. Store embeddings in a vector database or search index.
5. Retrieve relevant chunks for a user question.
6. Pass retrieved context to the model.
7. Generate an answer, ideally with citations or source references.
8. Evaluate retrieval quality and answer quality.

## Common Failure Modes

- Poor chunking loses meaning.
- Retrieval returns irrelevant context.
- The answer ignores the retrieved context.
- Source data is stale or low quality.
- The app lacks citations or confidence checks.
- The question requires data the corpus does not contain.

## Engineering Lens

RAG quality is usually constrained by retrieval before it is constrained by generation. Debug the search results before rewriting the answer prompt.

Design decisions to make explicit:

- What documents are trusted enough to index?
- How are chunks created and linked back to source locations?
- Is retrieval keyword, vector, hybrid, or filtered by metadata?
- What score or evidence threshold triggers "not found" behavior?
- How are stale documents removed or re-indexed?

## What To Evaluate

- Source hit rate for known-answer questions.
- Refusal behavior for out-of-corpus questions.
- Citation precision.
- Answer completeness from retrieved context.
- Retrieval robustness across synonyms and ambiguous queries.

## How To Explain By Audience

Developer: RAG is an application pattern that combines search, embeddings, context construction, generation, and evaluation.

Product stakeholder: RAG helps the AI answer from approved knowledge instead of relying only on what the model learned during training.

Strategic view: RAG is a way to make generative AI more useful and governable by connecting it to trusted knowledge.

## Explain It Back

Explain the difference between RAG and fine-tuning, including when you would choose each.
