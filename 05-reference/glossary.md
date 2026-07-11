# Glossary

## Models And Prompts

- Context window: the amount of input and output a model can consider at once.
- Fine-tuning: training a model further on examples to shape behavior or task performance.
- Foundation model: a broadly trained model that can be adapted to many tasks.
- Hallucination: an unsupported or false model output.
- Inference: generating an output from a model.
- Prompt: the instructions and input sent to a model.
- Structured output: a model response constrained to an application-readable shape such as a defined JSON schema.
- Temperature: a setting that influences output randomness.
- Token: a text unit processed by a model.

## Retrieval

- Chunking: splitting source documents into smaller pieces for retrieval.
- Citation precision: the degree to which cited sources actually support the associated answer claims.
- Embedding: a numeric representation of text used for similarity search.
- Grounding: providing source context so an answer is based on supplied information.
- Hybrid retrieval: combining lexical and vector search, often with metadata filters or reranking.
- RAG: retrieval-augmented generation, a pattern that retrieves relevant context before generation.
- Reranking: scoring retrieved candidates again to improve which results reach the model.
- Vector database: a store optimized for similarity search over embeddings.

## Agents And Tools

- Agent: an application pattern where a model can choose tools or actions to complete a goal.
- Agent harness: the runtime around a model that manages context, tools, permissions, execution loops, and computer or service access.
- Approval gate: an application-enforced pause requiring a human decision before a sensitive or mutating action.
- Harness: software that gives a model controlled access to context, tools, files, commands, or services and manages execution around it.
- Tool contract: the name, input schema, permissions, result shape, and error behavior exposed for a callable action.
- Tool calling: allowing a model-driven app to request specific external functions.

## Evaluation And Operations

- Evaluation: measuring whether outputs meet expected quality, safety, and task requirements.
- Evaluation runner: a system that applies fixed inputs and checks to candidate outputs; unlike an agent harness, it does not give a model tools or computer access.
- Golden set: a reviewed collection of representative inputs and expected behaviors used for regression evaluation.
- Human-in-the-loop: a workflow where a person reviews or owns a consequential decision rather than treating model output as final.
- Observability: request-level evidence—such as traces, latency, usage, validation, and error stages—used to understand system behavior.
- Prompt regression: a behavior that becomes worse after a prompt changes, detected by rerunning fixed evaluation cases.
- Rate limit: a bound on request frequency or usage over a time window.
- Recorded mode: an explicitly labeled path that displays committed example output without making a live provider call.
- Request id: a non-secret correlation identifier used to connect a user-visible failure with application or provider logs.
- Spend ceiling: an application-enforced aggregate limit intended to bound provider usage or cost.
- Telemetry: structured operational measurements emitted by a system, such as latency, token usage, mode, and validation outcome.

## Deployment And Security

- Authentication: verifying who or what is making a request.
- Authorization: deciding which actions or data an authenticated identity may access.
- CORS: browser-enforced rules controlling which origins may read responses from a web service.
- Fail closed: deny or stop an operation when a required safety control is unavailable.
- Kill switch: a configuration control that can disable a capability quickly without removing the deployment.
- Secret: a credential or sensitive value that must not be committed, logged, or exposed to browser code.
- Serverless function: request-driven compute managed by a cloud platform without a permanently running application server.
