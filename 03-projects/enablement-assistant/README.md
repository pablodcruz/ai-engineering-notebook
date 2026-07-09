# Enablement Assistant Prototype

A runnable RAG-style assistant over this notebook's markdown corpus. It is intentionally small, observable, and dependency-light so the retrieval and grounding behavior can be inspected without hiding behind infrastructure.

## Quick Start

PowerShell:

```powershell
cd 03-projects\enablement-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Bash or Git Bash:

```bash
cd 03-projects/enablement-assistant
python -m venv .venv
source .venv/Scripts/activate
pip install -e .
```

Ask a grounded question:

```powershell
enablement-assistant ask "What are common RAG failure modes?" --show-context
```

Run the evaluation set:

```powershell
enablement-assistant eval
```

Run tests:

```powershell
python -m unittest discover -s tests
```

## Commands

```powershell
enablement-assistant ask "How should projects be documented?"
enablement-assistant ask "What is the capital of France?"
enablement-assistant retrieve "chunking and metadata" --top-k 5
enablement-assistant index --out .cache\notebook-index.json
enablement-assistant eval --questions evals\questions.jsonl
```

## Prototype Boundary

This version uses local lexical retrieval and extractive answer synthesis. That keeps the core product behavior testable without external APIs. A production version can replace the retriever with embeddings and the synthesizer with a model gateway while preserving the same document, retrieval result, citation, and evaluation contracts.
