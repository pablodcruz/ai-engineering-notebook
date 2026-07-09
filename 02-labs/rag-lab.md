# RAG Lab

## Skill Level

Intermediate.

## Duration

45 to 90 minutes.

## Learning Objectives

- Explain the RAG pipeline.
- Build a small document-question answering workflow.
- Identify retrieval and generation failure modes.

## Minimal Build

Use a tiny corpus, such as three short markdown files, and build this flow:

1. Load documents.
2. Split into chunks.
3. Embed chunks.
4. Store chunks in a simple index.
5. Retrieve top matches for a question.
6. Send retrieved context to the model.
7. Return an answer with source references.

## Test Questions

- One answer directly present in the documents.
- One answer that requires combining two chunks.
- One answer not present in the documents.
- One ambiguous question.

## Common Failure Modes

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Wrong source retrieved | Chunking or query mismatch | Adjust chunk size, metadata, or retrieval query. |
| Answer ignores sources | Prompt does not require grounding | Require citations and "not found" behavior. |
| Good answer, no traceability | Missing source metadata | Preserve file names and chunk ids. |
| Confident wrong answer | Corpus lacks answer | Teach refusal or uncertainty path. |

## Build Notes

Pause after retrieval before generation. Many RAG problems are search problems before they are model problems.
