# Concepts

This folder explains the ideas that the runnable labs and projects put into practice. Each note answers three questions: what the pattern is, when it is appropriate, and what an engineer must evaluate around it.

## Reading Path

| Order | Concept | Practical question |
| --- | --- | --- |
| 1 | [LLM fundamentals](llm-fundamentals.md) | What is probabilistic, and what must the application control? |
| 2 | [Prompt engineering](prompt-engineering.md) | How do instructions become a versioned product contract? |
| 3 | [APIs, SDKs, and developer tools](apis-sdks-developer-tools.md) | How does a model call become a reliable integration? |
| 4 | [AI application workflows](ai-application-workflows.md) | Should this use prompting, retrieval, tools, or human review? |
| 5 | [RAG](rag.md) | How should answers use trusted external knowledge? |
| 6 | [Agents](agents.md) | Which actions can a model choose, and where must software enforce boundaries? |
| 7 | [Evaluation and observability](evaluation-observability.md) | How do we know behavior is good now and remains good after change? |
| 8 | [Cloud AI fundamentals](cloud-ai-fundamentals.md) | How does the system operate safely after deployment? |

## Concept-to-Evidence Map

| Concept | Lab | Strongest project evidence |
| --- | --- | --- |
| Prompt contracts | [Prompt engineering lab](../02-labs/prompt-engineering-lab.md) | [Prompt Regression Runner](../03-projects/prompt-regression-runner.md) |
| Provider integration | [API and SDK lab](../02-labs/api-sdk-integration-lab.md) | [Support Triage Review Console](../03-projects/live-support-triage-studio.md) |
| Grounding | [RAG lab](../02-labs/rag-lab.md) | [Enablement Assistant RAG](../03-projects/enablement-assistant-rag.md) |
| Tool boundaries | [Agent tool-use lab](../02-labs/agents-tool-use-lab.md) | [Agentic Workflow Demo](../03-projects/agentic-workflow-demo.md) |
| Troubleshooting | [Troubleshooting drills](../02-labs/troubleshooting-drills.md) | [Local AI Lab Runner](../03-projects/local-ai-lab-runner.md) |
| Human review | [AI application workflows](ai-application-workflows.md) | [Support Triage Review Console](../docs/support-triage.html) |

## Standard For A Useful Concept Note

A concept note should include:

- A plain explanation without product hype.
- The engineering decisions hidden by the simple explanation.
- Appropriate and inappropriate use cases.
- Failure modes and evaluation questions.
- A link to runnable evidence in this repository.
- A short explain-it-back prompt for teaching practice.

These notes are not substitutes for provider documentation. They capture durable system-design understanding; current API fields, model availability, pricing, and service limits should always be checked against official documentation when implementing.
