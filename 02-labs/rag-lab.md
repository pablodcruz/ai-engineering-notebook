# RAG Lab

## Skill Level

Intermediate.

## Duration

45 to 90 minutes.

## Learning Objectives

- Explain the RAG pipeline.
- Build a small document-question answering workflow.
- Identify retrieval and generation failure modes.
- Show retrieved context before producing an answer.

## Prerequisites

- Python 3.10 or newer.
- A small trusted markdown corpus, such as three short notes.
- Basic familiarity with embeddings, retrieval, and source citations.
- Optional: model API credentials if you add a live generation step.

## Setup

1. Create a working folder for the lab.
2. Add three small markdown documents to a `corpus/` folder.
3. Prepare a script or notebook with functions for loading, chunking, retrieval, and answering.
4. Keep a test question list nearby so every change can be checked against the same prompts.

## Exercise

Use the tiny corpus to build this flow:

1. Load documents.
2. Split them into chunks.
3. Preserve metadata: file name, heading, and chunk id.
4. Embed or score chunks.
5. Store chunks in a simple index.
6. Retrieve top matches for a question.
7. Print retrieved chunks before generating an answer.
8. Return an answer with source references.
9. Return "not found in sources" when the answer is not covered by the corpus.

## Expected Output

The lab should produce:

- A retrieved chunk list with scores or ranks.
- A grounded answer with at least one source reference.
- A refusal for an uncovered question.
- A short note explaining one retrieval failure and the likely fix.

Use these test questions:

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
| Evaluation feels subjective | No fixed test set | Save questions, expected sources, and expected answer traits. |

## Build Notes

Pause after retrieval before generation. Many RAG problems are search problems before they are model problems. Treat chunk inspection as a required debugging step, not an optional trace.

## Debrief

- Which test question retrieved the best source most reliably?
- Which question failed, and was it a retrieval problem or an answer-generation problem?
- Did the answer cite the right source, or merely a plausible source?
- What would you change before using this pattern with a larger document set?
