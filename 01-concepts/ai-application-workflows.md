# AI Application Workflows

## Why This Matters

Explain common patterns for turning model capabilities into usable software.

## Workflow 1: Prompted Task

Use when the application needs summarization, classification, rewriting, extraction, or drafting.

Flow:

1. Collect user input.
2. Add task instructions and constraints.
3. Call the model.
4. Validate or parse the output.
5. Show the result to the user.

## Workflow 2: Grounded Question Answering

Use when answers need to come from a specific knowledge base.

Flow:

1. Index trusted content.
2. Retrieve relevant context.
3. Ask the model to answer from that context.
4. Include sources.
5. Handle "not found" cases.

## Workflow 3: Tool-Using Assistant

Use when the application needs to take steps across systems.

Flow:

1. Define allowed tools.
2. Give the model a goal and constraints.
3. Execute tool calls through application code.
4. Feed observations back to the model.
5. Stop, summarize, or ask for user confirmation.

## Workflow 4: Human-In-The-Loop Review

Use when output affects customers, compliance, money, or operations.

Flow:

1. Generate a draft or recommendation.
2. Show evidence or reasoning trace where appropriate.
3. Let a human approve, edit, or reject.
4. Capture feedback.
5. Improve prompts, retrieval, or evaluation.

## Production Concerns

- Security and access control.
- Data privacy.
- Cost and latency.
- Evaluation.
- Monitoring.
- Fall-back behavior.
- User experience.
- Change management.

## Engineering Lens

Choose the simplest workflow that creates enough reliability for the job. A prompted task, a RAG flow, and an agent are not maturity levels; they are different architectures with different risks.

Decision rule:

- Use prompted tasks when the input already contains enough information.
- Use RAG when the answer must come from trusted external knowledge.
- Use tools when the workflow needs current state or external actions.
- Use human review when the output affects customers, compliance, money, or operations.

## What To Evaluate

- Whether the chosen workflow matches the user's risk level.
- Which step is most likely to fail.
- What evidence the user sees before trusting output.
- How the workflow behaves when data is missing.
- What should be automated and what should remain human-approved.

## Build Drill

Pick one workflow and turn it into a small runnable demo.
